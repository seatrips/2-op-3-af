from datetime import datetime, timedelta
import json

def generate_schedule_html():
    # Ask for the name of the person
    person_name = input("Enter the name of the person: ")
    
    # Ask for the start date
    while True:
        start_date_str = input("Enter the start date (YYYY-MM-DD, starting on a Tuesday): ")
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if start_date.weekday() != 1:
                print("The start date must be a Tuesday. Please try again.")
            else:
                break
        except ValueError:
            print("Invalid date format. Please enter the date in YYYY-MM-DD format.")

    # Define the on and off periods
    on_duration = timedelta(weeks=2)
    off_duration = timedelta(weeks=3)

    # Initialize the schedule list and calendar data
    schedule = []
    calendar_data = {}

    # Labels and colors for different scenarios
    labels = ["ON", "OFF", "Scenario Training", "Medical", "Sick", "Course", "FOG"]
    colors = ["#ffcccc", "#ccffcc", "#FFD700", "#87CEFA", "#FF6347", "#90EE90", "#D3D3D3"]

    # Loop to generate schedule for one year (365 days)
    current_date = start_date
    while current_date.year == start_date.year:
        end_on_date = current_date + on_duration - timedelta(days=1)
        if end_on_date.year != start_date.year:
            end_on_date = datetime(start_date.year, 12, 31)

        schedule.append({
            'start': current_date,
            'end': end_on_date,
            'status': 'ON'
        })

        # Fill calendar data for ON period
        delta = timedelta(days=1)
        while current_date <= end_on_date:
            calendar_data[current_date.strftime('%Y-%m-%d')] = {
                'label': 'ON',
                'color': colors[0]
            }
            current_date += delta

        if current_date.year != start_date.year:
            break

        # Skip to the next Tuesday for the start of the Off period
        while current_date.weekday() != 1:
            current_date += timedelta(days=1)

        end_off_date = current_date + off_duration - timedelta(days=1)
        if end_off_date.year != start_date.year:
            end_off_date = datetime(start_date.year, 12, 31)

        schedule.append({
            'start': current_date,
            'end': end_off_date,
            'status': 'OFF'
        })

        # Fill calendar data for OFF period
        while current_date <= end_off_date:
            calendar_data[current_date.strftime('%Y-%m-%d')] = {
                'label': 'OFF',
                'color': colors[1]
            }
            current_date += delta

    # Generate HTML
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Schedule for {name} - {year}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2 {{
                color: #2c3e50;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .on {{ background-color: #ffcccc; }}
            .off {{ background-color: #ccffcc; }}
            button {{
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                margin: 10px 10px 10px 0;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #2980b9;
            }}
            #clearCalendar {{
                background-color: #e74c3c;
            }}
            #clearCalendar:hover {{
                background-color: #c0392b;
            }}
            .legend {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 20px;
            }}
            .scenario {{
                display: flex;
                align-items: center;
                cursor: pointer;
            }}
            .scenario-color {{
                width: 20px;
                height: 20px;
                margin-right: 10px;
            }}
            .calendar-day {{
                cursor: pointer;
                position: relative;
                height: 60px;
                width: 60px;
            }}
            .calendar-day:hover {{
                opacity: 0.8;
            }}
            .month-name {{
                background-color: #34495e;
                color: white;
            }}
            .cell-text {{
                font-size: 10px;
                position: absolute;
                bottom: 2px;
                left: 2px;
                right: 2px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }}
        </style>
        <script>
            const labels = {labels};
            const colors = {colors};
            let selectedLabel = null;
            let initialCalendarData = {initial_calendar_data};

            function initializeCalendar() {{
                const calendarData = JSON.parse(localStorage.getItem('calendarData')) || initialCalendarData;
                Object.entries(calendarData).forEach(([date, data]) => {{
                    const cell = document.getElementById(date);
                    if (cell) {{
                        cell.style.backgroundColor = data.color;
                        cell.title = data.label;
                        if (data.text) {{
                            cell.querySelector('.cell-text').textContent = data.text;
                        }}
                    }}
                }});
                localStorage.setItem('calendarData', JSON.stringify(calendarData));
            }}

            function selectLabel(label) {{
                selectedLabel = label;
                document.querySelectorAll('.scenario').forEach(el => el.style.fontWeight = 'normal');
                event.currentTarget.style.fontWeight = 'bold';
            }}

            function updateCalendar(date) {{
                const cell = document.getElementById(date);
                const calendarData = JSON.parse(localStorage.getItem('calendarData')) || {{}};

                if (cell.style.backgroundColor && (!selectedLabel || cell.title !== selectedLabel)) {{
                    // If the cell has a color and either no label is selected or a different label is selected, clear it
                    cell.style.backgroundColor = '';
                    cell.title = '';
                    delete calendarData[date];
                }} else if (selectedLabel) {{
                    // If a label is selected, apply the color
                    const color = colors[labels.indexOf(selectedLabel)];
                    cell.style.backgroundColor = color;
                    cell.title = selectedLabel;
                    calendarData[date] = {{
                        'label': selectedLabel,
                        'color': color,
                        'text': calendarData[date] ? calendarData[date].text : ''
                    }};
                }}

                // Prompt for text input
                const text = prompt("Enter text for this date (leave empty to clear):", calendarData[date] ? calendarData[date].text : '');
                if (text !== null) {{  // user didn't cancel the prompt
                    if (text) {{
                        calendarData[date] = calendarData[date] || {{}};
                        calendarData[date].text = text;
                        cell.querySelector('.cell-text').textContent = text;
                    }} else {{
                        if (calendarData[date]) {{
                            delete calendarData[date].text;
                        }}
                        cell.querySelector('.cell-text').textContent = '';
                    }}
                }}

                localStorage.setItem('calendarData', JSON.stringify(calendarData));
            }}
            
            function saveToJSON() {{
                const calendarData = JSON.parse(localStorage.getItem('calendarData')) || {{}};
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(calendarData, null, 2));
                const downloadAnchorNode = document.createElement('a');
                downloadAnchorNode.setAttribute("href", dataStr);
                downloadAnchorNode.setAttribute("download", "calendar_data.json");
                document.body.appendChild(downloadAnchorNode);
                downloadAnchorNode.click();
                downloadAnchorNode.remove();
            }}

            function clearCalendar() {{
                if (confirm("Are you sure you want to clear all calendar entries?")) {{
                    localStorage.setItem('calendarData', JSON.stringify(initialCalendarData));
                    document.querySelectorAll('.calendar-day').forEach(cell => {{
                        const date = cell.id;
                        if (initialCalendarData[date]) {{
                            cell.style.backgroundColor = initialCalendarData[date].color;
                            cell.title = initialCalendarData[date].label;
                            cell.querySelector('.cell-text').textContent = '';
                        }} else {{
                            cell.style.backgroundColor = '';
                            cell.title = '';
                            cell.querySelector('.cell-text').textContent = '';
                        }}
                    }});
                    console.log("Calendar cleared and reset to initial state");
                }}
            }}

            window.onload = initializeCalendar;
        </script>
    </head>
    <body>
        <h1>Schedule for {name} - {year}</h1>
        <button onclick="window.print()">Print Schedule</button>
        <button onclick="saveToJSON()">Save Calendar Data to JSON</button>
        <button id="clearCalendar" onclick="clearCalendar()">Reset Calendar</button>
        
        <h2>Work Schedule</h2>
        <table>
            <tr>
                <th>Start Date</th>
                <th>End Date</th>
                <th>Status</th>
            </tr>
    """.format(
        name=person_name, 
        year=start_date.year,
        labels=json.dumps(labels), 
        colors=json.dumps(colors),
        initial_calendar_data=json.dumps(calendar_data)
    )

    for period in schedule:
        status_class = 'on' if period['status'] == 'ON' else 'off'
        html_content += """
            <tr class="{status_class}">
                <td>{start}</td>
                <td>{end}</td>
                <td>{status}</td>
            </tr>
        """.format(start=period['start'].strftime('%Y-%m-%d'), 
                   end=period['end'].strftime('%Y-%m-%d'), 
                   status=period['status'],
                   status_class=status_class.lower())

    html_content += """
        </table>
        
        <h2>Year Calendar</h2>
        <div class="legend">
            {legend}
        </div>
        <table>
    """.format(
        legend=''.join([f'<div class="scenario" onclick="selectLabel(\'{label}\')"><div class="scenario-color" style="background-color: {colors[i]};"></div>{label}</div>' for i, label in enumerate(labels)])
    )

    # Create calendar
    for month in range(1, 13):
        month_name = datetime(start_date.year, month, 1).strftime('%B')
        html_content += f'<tr><th colspan="7" class="month-name">{month_name}</th></tr><tr>'
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            html_content += f"<th>{day}</th>"
        html_content += "</tr><tr>"

        first_day = datetime(start_date.year, month, 1)
        start_weekday = first_day.weekday()
        
        for _ in range(start_weekday):
            html_content += "<td></td>"

        for day in range(1, 32):
            try:
                current_date = datetime(start_date.year, month, day)
                date_str = current_date.strftime('%Y-%m-%d')
                html_content += f'<td id="{date_str}" class="calendar-day" onclick="updateCalendar(\'{date_str}\')">{day}<div class="cell-text"></div></td>'

                if current_date.weekday() == 6:
                    html_content += "</tr><tr>"
            except ValueError:
                break

        html_content += "</tr>"

    html_content += """
        </table>
    </body>
    </html>
    """

    # Save the HTML content to a file
    file_name = "schedule_{}_{}.html".format(person_name.replace(" ", "_"), start_date.year)
    with open(file_name, "w") as file:
        file.write(html_content)

    print(f"Schedule for {person_name} ({start_date.year}) generated and saved as {file_name}")

# Run the function
generate_schedule_html()