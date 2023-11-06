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

app.get('/api/requirements', (req, res) => {
  let db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      console.error(err.message);
      res.status(500).send('Error connecting to the database');
    }
  });

  const sql = 'SELECT * FROM requirement_similarities';
  
  db.all(sql, [], (err, rows) => {
    if (err) {
      res.status(500).send('Error executing the query');
    } else {
      res.json(rows);
    }
  });

  db.close();
});

const server = app.listen(port, () => console.log(`Example app listening on port ${port}!`));

server.keepAliveTimeout = 120 * 1000;
server.headersTimeout = 120 * 1000;