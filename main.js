const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql');
const app = express();
app.use(bodyParser.json());

var hostname = "4rl.h.filess.io";
var database = "sampledb_battleland";
var port = "3307";
var username = "sampledb_battleland";
var password = "d41fc9d600798d0566c85dcc6d62f6096e8b41d5";

var db = mysql.createConnection({
  host: hostname,
  user: username,
  password,
  database,
  port,
});

db.connect(function (err) {
  if (err) throw err;
  console.log("Connected!");
});

db.query("SELECT 1+1").on("result", function (row) {
  console.log(row);
});


// Route for displaying last week leaderboard for a given country

app.get('/current_week', (req, res) => {
    const current_date = new Date();
    const startWeekdate = new Date(current_date.getFullYear(), current_date.getMonth(), current_date.getDate() - current_date.getDay());

    // Format the startOfWeek to match the format of your timestamp column
    const formattedStartOfWeek = startWeekdate.toISOString().split('T')[0];

    db.query(`SELECT * FROM score_table WHERE DATE(TimeStamp) >= '${formattedStartOfWeek}' ORDER BY Score DESC LIMIT 200`, (error, results) => {
        if (error) throw error;
        res.json(results);
    });
   });

   app.get('/last_week/:country', (req, res) => {
    const { country } = req.params;

    if (!country) {
        return res.status(400).json({ error: 'Country parameter is required' });
    }

    const current_date = new Date();
    const startWeekdate = new Date(current_date.getFullYear(), current_date.getMonth(), current_date.getDate() - current_date.getDay());
    const lastWeekdate = new Date(startWeekdate);
    lastWeekdate.setDate(lastWeekdate.getDate() - 7);

    // Format the startOfWeek and lastWeekStart to match the format of your timestamp column
    const formattedStartWeekdate = startWeekdate.toISOString().split('T')[0];
    const formattedLastWeekStart = lastWeekdate.toISOString().split('T')[0];

    db.query(`SELECT * FROM score_table WHERE DATE(TimeStamp) >= '${formattedLastWeekStart}' AND DATE(TimeStamp) < '${formattedStartWeekdate}' AND Country = '${country}' ORDER BY Score DESC LIMIT 200`, (error, results) => {
        if (error) throw error;
        res.json(results);
    });
});



// Route for fetching user rank
app.get('/user_rank/:us_id', (req, res) => {
    const { us_id } = req.params;

    if (!us_id) {
        return res.status(400).json({ error: 'User ID parameter is required' });
    }

    db.query(`SELECT t.Rank FROM (SELECT UID, RANK() OVER (ORDER BY Score DESC) as 'Rank' FROM score_table) t WHERE t.UID = ?;`, [us_id], (error, results) => {
        if (error) throw error;

        if (results.length > 0) {
            const userRank = results[0].Rank;
            res.json({ userRank });
        } else {
            res.status(404).json({ error: 'User not found' });
        }
    });
});



app.listen(3000, () => {
    console.log(`Server is running on port ${port}`);
});
