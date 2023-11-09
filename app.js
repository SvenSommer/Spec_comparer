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
        GROUP_CONCAT(DISTINCT s.id) as ids
      FROM 
        specifications s
      LEFT JOIN 
        requirements r ON s.id = r.specification_id
      GROUP BY 
        s.name`;

  db.all(sql, [], (err, rows) => {
    if (err) {
      res.status(500).send('Error executing the query');
    } else {
      // Transformieren Sie die kommagetrennte Liste in Arrays für die Antwort
      const transformedRows = rows.map(row => ({
        ...row,
        versions: row.versions ? row.versions.split(',') : [],
        ids: row.ids ? row.ids.split(',').map(id => parseInt(id, 10)) : []
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
    SELECT * FROM requirement_similarities 
    WHERE spec1_id = ? AND spec2_id = ?
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

  // Hier nehmen wir an, dass die IDs als Abfrageparameter in der Form "ids=1&ids=2&..." übergeben werden.
  const specIds = req.query.ids;
  if (!specIds || !Array.isArray(specIds) || specIds.length === 0) {
    res.status(400).send('No specification IDs provided');
    return;
  }

  // Erstellen Sie die SQL-Abfrage, um die Daten basierend auf den übergebenen IDs zu filtern.
  const placeholders = specIds.map(() => '?').join(',');
  const sql = `
    SELECT 
      rs.spec1_id, 
      s1.name as spec1_name, 
      s1.version as spec1_version, 
      rs.spec2_id, 
      s2.name as spec2_name, 
      s2.version as spec2_version, 
      COUNT(*) as similarity_count
    FROM 
      requirement_similarities rs
    JOIN 
      specifications s1 ON rs.spec1_id = s1.id
    JOIN 
      specifications s2 ON rs.spec2_id = s2.id
    WHERE 
      rs.spec1_id IN (${placeholders}) AND rs.spec2_id IN (${placeholders})
    GROUP BY 
      rs.spec1_id, rs.spec2_id
  `;

  // Führe die SQL-Abfrage mit den IDs als Parameter aus.
  db.all(sql, [...specIds, ...specIds], (err, rows) => {
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