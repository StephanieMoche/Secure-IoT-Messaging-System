
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Heart Rate Data</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }

        th, td {
            border: 1px solid #cccccc;
            padding: 10px;
            text-align: left;
        }

        th {
            background-color: #f2f2f2;
        }

        input, button {
            padding: 8px;
        }

        tr:nth-child(even) {
            background-color: #fafafa;
        }
    </style>
</head>

<body>

    <h1>Heart Rate Data</h1>

    <form method="GET" action="/">
        <input
            type="text"
            name="name"
            placeholder="Search by name"
            value="{{name}}"
        >

        <button type="submit">Search</button>

        <a href="/">Clear</a>
    </form>

    <p>Simulated heart-rate readings (UTC)</p>

    <table>
        <thead>
            <tr>
                <th>Device ID</th>
                <th>Heart Rate (bpm)</th>
                <th>Timestamp</th>
            </tr>
        </thead>

        <tbody>
            % for reading in readings:
                <tr>
                    <td>{{reading['device_id']}}</td>
                    <td>{{reading['heart_rate']}}</td>
                    <td>{{reading['timestamp']}}</td>
                </tr>
            % end

            % if not readings:
                <tr>
                    <td colspan="3">No readings found.</td>
                </tr>
            % end
        </tbody>
    </table>

</body>
</html>
