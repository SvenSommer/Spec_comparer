const express = require("express");
const app = express();
const port = process.env.PORT || 3001;

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const dbPath = path.resolve(__dirname, 'public/db/requirements.db');

app.use(express.static('public'));
const cors = require('cors');
app.use(cors());
app.get("/", (req, res) => res.type('html').send(html));

app.get('/api/specifications', (req, res) => {
  let db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      console.error(err.message);
      res.status(500).send('Error connecting to the database');
      return;
    }
  });

  const sql = `
        SELECT 
          s.name, 
          GROUP_CONCAT(DISTINCT s.version) as versions, 
          GROUP_CONCAT(DISTINCT s.id) as ids,
          GROUP_CONCAT(DISTINCT s.status) as status,
          GROUP_CONCAT(DISTINCT t.name) as types,
          GROUP_CONCAT(DISTINCT c.name) as categories,
          GROUP_CONCAT(DISTINCT t.id) as type_ids,
          GROUP_CONCAT(DISTINCT c.id) as category_ids
        FROM 
          specifications s
        LEFT JOIN 
          requirements r ON s.id = r.specification_id
        LEFT JOIN 
          spec_types t ON s.type_id = t.id
        LEFT JOIN 
          spec_categories c ON s.category_id = c.id
        GROUP BY 
          s.name`;

  db.all(sql, [], (err, rows) => {
    if (err) {
      res.status(500).send('Error executing the query');
    } else {
      // Transform the comma-separated lists into arrays for the response
      const transformedRows = rows.map(row => ({
        ...row,
        versions: row.versions ? row.versions.split(',') : [],
        ids: row.ids ? row.ids.split(',').map(id => parseInt(id, 10)) : [],
        types: row.types ? row.types.split(',') : [],
        categories: row.categories ? row.categories.split(',') : [],
        type_ids: row.type_ids ? row.type_ids.split(',').map(id => parseInt(id, 10)) : [],
        category_ids: row.category_ids ? row.category_ids.split(',').map(id => parseInt(id, 10)) : []
      }));
      res.json(transformedRows);
    }
  });

  db.close();
});



app.get('/api/requirements', (req, res) => {
  const spec1Id = req.query.spec1Id;
  const spec2Id = req.query.spec2Id;

  let db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      console.error(err.message);
      res.status(500).send('Error connecting to the database');
      return;
    }
  });

  const sql = `
        SELECT 
        r1.requirement_number as req1_requirement_number,
        source1.name AS req1_source, 
        r1.title AS spec1_title, 
        r1.description AS spec1_description, 
        obligation1.name AS spec1_obligation, 
        test1.name AS spec1_test_procedure,
        r2.requirement_number as req2_requirement_number,
        r2.title AS spec2_title, 
        r2.description AS spec2_description, 
        source2.name AS req2_source, 
        obligation2.name AS spec2_obligation, 
        test2.name AS spec2_test_procedure,
        rs.comparison_method_id as comparison_method,
        rs.title_similarity_score,
        rs.description_similarity_score,
        rs.combined_identifier
      FROM 
        requirement_similarities rs
      JOIN 
        requirements r1 ON rs.requirement1_id = r1.id
      JOIN 
        requirements r2 ON rs.requirement2_id = r2.id
      JOIN 
        req_sources source1 ON r1.source_id = source1.id
      JOIN 
        req_sources source2 ON r2.source_id = source2.id
      JOIN 
        req_obligations obligation1 ON r1.obligation_id = obligation1.id
      JOIN 
        req_obligations obligation2 ON r2.obligation_id = obligation2.id
      JOIN 
        req_test_procedures test1 ON r1.test_procedure_id = test1.id
      JOIN 
        req_test_procedures test2 ON r2.test_procedure_id = test2.id
      WHERE 
        r1.specification_id = ? AND 
        r2.specification_id = ?
  `;

  db.all(sql, [spec1Id, spec2Id], (err, rows) => {
    if (err) {
      res.status(500).send('Error executing the query');
    } else {
      res.json(rows);
    }
  });

  db.close();
});


app.get('/api/matrix', (req, res) => {
  let db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      console.error(err.message);
      res.status(500).send('Error connecting to the database');
      return;
    }
  });

  let specIds = req.query.ids;
  const threshold = req.query.threshold || '0.75'; // Default threshold value if not provided

  if (!specIds || !Array.isArray(specIds) || specIds.length < 2) {
    res.status(400).send('At least two specification IDs are required');
    return;
  }

  // Ensure all specIds are numbers to prevent SQL injection
  specIds = specIds.map(Number);
  if (specIds.some(isNaN)) {
    res.status(400).send('All specification IDs must be numbers');
    return;
  }

  // Generate all unique pairs of specIds for the WHERE clause
  const pairs = [];
  for (let i = 0; i < specIds.length; i++) {
    for (let j = i + 1; j < specIds.length; j++) {
      pairs.push(`(rs.specification1_id = ${specIds[i]} AND rs.specification2_id = ${specIds[j]})`);
    }
  }
  const wherePairs = pairs.join(' OR ');

  const thresholdValue = parseFloat(threshold);
  if (isNaN(thresholdValue) || thresholdValue < 0.20 || thresholdValue > 1) {
    res.status(400).send('Invalid threshold value');
    return;
  }

  const sql = `
  SELECT 
  s1.id AS spec1_id,
  s1.name AS spec1_name,
  s1.version AS spec1_version,
  s1.req_count AS spec1_req_count,
  COALESCE(COUNT(DISTINCT rs.requirement1_number), 0) AS spec1_unique_requirements,
  s2.id AS spec2_id,
  s2.name AS spec2_name,
  s2.version AS spec2_version,
  s2.req_count AS spec2_req_count,
  COALESCE(COUNT(DISTINCT rs.requirement2_number), 0) AS spec2_unique_requirements
FROM 
  requirement_similarities rs
JOIN 
  specifications s1 ON rs.specification1_id = s1.id
JOIN 
  specifications s2 ON rs.specification2_id = s2.id
WHERE 
  rs.description_similarity_score >= ? AND (${wherePairs})
GROUP BY 
  s1.id, s2.id

  `;

  db.all(sql, [thresholdValue], (err, rows) => {
    if (err) {
      console.error(err.message);
      res.status(500).send('Error executing the query');
    } else {
      res.json(rows);
    }
    db.close();
  });
});


app.get('/api/specs', (req, res) => {
  let db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      console.error(err.message);
      res.status(500).send('Error connecting to the database');
      return;
    }
  });

  const specIds = req.query.ids;
  if (!specIds || !Array.isArray(specIds) || specIds.length === 0) {
    res.status(400).send('No specification IDs provided');
    return;
  }

  const placeholders = specIds.map(() => '?').join(',');
  const sql = `
    SELECT id, name, version
    FROM specifications
    WHERE id IN (${placeholders})
  `;

  db.all(sql, specIds, (err, rows) => {
    if (err) {
      console.error(err.message);
      res.status(500).send('Error executing the query');
    } else {
      res.json(rows);
    }
    db.close();
  });
});



const server = app.listen(port, () => console.log(`Example app listening on port ${port}!`));

server.keepAliveTimeout = 120 * 1000;
server.headersTimeout = 120 * 1000;