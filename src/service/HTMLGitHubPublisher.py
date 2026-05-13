import os
import stat
import logging
import tempfile
import shutil
import pandas as pd
from git import Repo
from datetime import datetime

class HTMLGitHubPublisher():

    def __init__(self):

        self._CLASS_COLORS = {
                "Deathknight": "#C41F3B",
                "Demon Hunter": "#A330C9",
                "Druid": "#FF7D0A",
                "Hunter": "#ABD473",
                "Mage": "#69CCF0",
                "Monk": "#00FF96",
                "Paladin": "#F58CBA",
                "Priest": "#FFFFFF",
                "Rogue": "#FFF569",
                "Shaman": "#0070DE",
                "Warlock": "#9482C9",
                "Warrior": "#C79C6E",
        }

        self._logger = logging.getLogger()
        self._logger.info("Initializing HTMLGitHubPublisher instance")

    def publish_list(self, raid_type, raid_id, attendance_list, context):
        
        self._logger.info(f"[{context.username}]: Invoked 'publish_list' from HTMLGitHubPublisher")

        tmp_dir = tempfile.mkdtemp()
        GITHUB_REPO_URL = (
            f"https://{os.getenv('GITHUB_USER')}:"
            f"{os.getenv('GITHUB_TOKEN')}"
            f"@github.com/{os.getenv('GITHUB_USER')}/gda-attendance-raid-list-tables.git"
        )

        final_link = None

        try:
            self._logger.debug(f"[{context.username}]: Starting repository clone...")
            repo = Repo.clone_from(GITHUB_REPO_URL, tmp_dir)
            self._logger.debug(f"[{context.username}]: Repository cloned successfully")

            folder_server_path = os.path.join(tmp_dir, context.server)
            os.makedirs(folder_server_path, exist_ok=True)
            guild_folder_path = os.path.join(folder_server_path, context.guild_id)
            os.makedirs(guild_folder_path, exist_ok=True)

            html_content = self._create_html_content(raid_id=raid_id, attendance_list=attendance_list, context=context, date=datetime.now().timestamp())
            html_path = os.path.join(guild_folder_path, f"{raid_type}_{raid_id}.html")
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            self._logger.debug(f"[{context.username}]: Table saved in {html_path}")

            repo.index.add([html_path])
            self._logger.debug(f"[{context.username}]: File added to index")
            repo.index.commit("Update Attendance List")
            self._logger.debug(f"[{context.username}]: Commit completed")

            origin = repo.remote(name="origin")
            self._logger.debug(f"[{context.username}]: Starting push...")
            origin.push()
            self._logger.debug(f"[{context.username}]: Push completed")
            repo.close()
            final_link = (f"{os.getenv('GITHUB_ATTENDANCE_LIST_SITE')}{context.server}/{context.guild_id}/{raid_type}_{raid_id}.html").replace(" ", "%20")

            self._logger.info(f"[{context.username}]: Attendance list published successfully")
            self._logger.info(f"[{context.username}]: Final link: {final_link}")

        except Exception as e:
            self._logger.error(f"[{context.username}]: Error publishing attendance list: {e}")
            raise e
        finally:
            def remove_readonly(func, path, excinfo):
                os.chmod(path, stat.S_IWRITE)
                func(path)

            shutil.rmtree(tmp_dir, onerror=remove_readonly)

        return final_link

    def _create_html_content(self, raid_id, attendance_list, context, date):

        self._logger.info(
            f"[{context.username}]: Invoked '_create_html_content' from HTMLGitHubPublisher"
        )

        _table_data = []

        for attendance in attendance_list:

            name = attendance.name
            item_name = attendance.item
            item_id = attendance.item_id
            score = attendance.score
            player_class = attendance.char_class

            color = self._CLASS_COLORS.get(player_class, "#FFFFFF")

            name_html = (
                f'<a href="https://www.chromiecraft.com/en/armory/?character/ChromieCraft/{name}" '
                f'target="_blank" style="color:{color};">'
                f'{name.capitalize()}</a>'
            )

            item_html = (
                f'<a href="https://www.wowhead.com/wotlk/item={item_id}" '
                f'data-wowhead="item={item_id}&tooltip=right" '
                f'style="color:#CCAA00;text-decoration:none;">'
                f'{item_name}</a>'
            )

            _table_data.append([name_html, item_html, score])

        headers = ["Player", "Reserve", "Score"]

        df = pd.DataFrame(_table_data, columns=headers)

        table_html = df.to_html(
            index=False,
            classes="attendance-table",
            border=0,
            escape=False
        )

        logo_url = os.getenv("GITHUB_LOGO_URL")
        gif_url = os.getenv("GITHUB_DANCE_GIF_URL")
        chromie_logo = os.getenv("GITHUB_CHROMIE_LOGO_URL")
        wow_wallpaper = os.getenv("GITHUB_WOW_WALLPAPER_URL")

        raid_name = os.getenv(raid_id.upper())

        formatted_date = datetime.fromtimestamp(date).strftime("%d/%m/%Y %H:%M")

        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">

        <head>

            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <title>{raid_name} - Attendance List</title>

            <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap" rel="stylesheet">

            <style>

                html, body {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}

                body {{
                    font-family: Arial, sans-serif;
                    background-image: url('{wow_wallpaper}');
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                    color: #fff;
                    min-height: 100%;
                }}

                header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 20px 40px;
                }}

                .header-left img,
                .header-right img {{
                    height: 90px;
                    border-radius: 12px;
                }}

                .table-title {{
                    text-align: center;
                    font-family: 'Cinzel', serif;
                    font-size: 2.3em;
                    font-weight: 700;
                    margin: 10px 0 5px 0;
                    color: #CCAA00;
                    letter-spacing: 1.5px;
                    animation: pulseGlow 5s ease-in-out infinite;
                }}

                .last-update {{
                    text-align: center;
                    font-family: Arial, sans-serif;
                    font-size: 0.95em;
                    color: #CCAA00;
                    margin-bottom: 18px;
                    opacity: 0.9;
                }}

                @keyframes pulseGlow {{
                    0%, 100% {{
                        text-shadow: none;
                    }}

                    25% {{
                        text-shadow:
                            0 0 4px rgba(204,170,0,0.4),
                            0 0 10px rgba(204,170,0,0.3);
                    }}

                    50% {{
                        text-shadow:
                            0 0 6px rgba(204,170,0,0.6),
                            0 0 14px rgba(204,170,0,0.45),
                            0 0 24px rgba(204,170,0,0.35);
                    }}

                    75% {{
                        text-shadow:
                            0 0 4px rgba(204,170,0,0.4),
                            0 0 10px rgba(204,170,0,0.3);
                    }}
                }}

                .search-container {{
                    width: 80%;
                    margin: 0 auto 10px;
                    display: flex;
                    justify-content: flex-end;
                }}

                .search-container input {{
                    padding: 6px 10px;
                    font-size: 1em;
                    border-radius: 6px;
                    border: 2px solid #CCAA00;
                    background-color: rgba(0,0,0,0.8);
                    color: #CCAA00;
                    outline: none;
                    width: 220px;
                }}

                .search-container input::placeholder {{
                    color: #CCAA00;
                    opacity: 0.7;
                }}

                .attendance-table {{
                    width: 80%;
                    margin: 0 auto 40px auto;
                    border-collapse: collapse;
                    background-color: rgba(17,17,17,0.85);
                    box-shadow: 0px 2px 5px rgba(255,255,255,0.1);
                    border-top: 2px solid #CCAA00;
                    border-bottom: 2px solid #CCAA00;
                    cursor: default;
                }}

                .attendance-table th {{
                    background-color: #CCAA00;
                    color: #000;
                    padding: 12px;
                    font-size: 1.05em;
                    text-align: left;
                    font-family: Arial, sans-serif;
                    transition: all 0.3s ease;
                    cursor: pointer;
                    position: relative;
                }}

                .attendance-table th:hover {{
                    box-shadow: inset 0 0 10px rgba(204, 170, 0, 0.4);
                }}

                .attendance-table th .sort-arrow {{
                    margin-left: 6px;
                    font-size: 0.8em;
                    color: #000;
                }}

                .attendance-table td {{
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #333;
                    font-family: Arial, sans-serif;
                    transition: all 0.3s ease;
                }}

                .attendance-table tr:last-child td {{
                    border-bottom: none;
                }}

                .attendance-table tr:hover {{
                    background-color: rgba(34,34,34,0.9);
                    box-shadow: inset 0 0 10px rgba(204, 170, 0, 0.4);
                }}

                .bottom-message {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-top: 30px;
                    gap: 10px;
                    font-family: Arial, sans-serif;
                }}

                .small-gif {{
                    width: 100px;
                    height: auto;
                    border-radius: 6px;
                }}

            </style>

        </head>

        <body>

            <header>

                <div class="header-left">
                    <img src="{logo_url}" alt="GDA Logo">
                </div>

                <div class="header-right">
                    <img src="{chromie_logo}" alt="Chromie">
                </div>

            </header>

            <div class="table-title">
                {raid_name} - Attendance List
            </div>

            <div class="last-update">
                Last Update: {formatted_date}
            </div>

            <div class="search-container">
                <input type="text" id="searchInput" placeholder="Search...">
            </div>

            {table_html}

            <div class="bottom-message">
                <img class="small-gif" src="{gif_url}" alt="Dancing GIF">
                <span><strong>Thanks for joining us!</strong></span>
            </div>

            <script src="https://wow.zamimg.com/widgets/power.js"></script>

            <script>

                const searchInput = document.getElementById('searchInput');
                const table = document.querySelector('.attendance-table');
                const tbody = table.tBodies[0];

                searchInput.addEventListener('input', () => {{

                    const filter = searchInput.value.toLowerCase();

                    Array.from(tbody.rows).forEach(row => {{

                        const rowText = row.innerText.toLowerCase();

                        row.style.display = rowText.includes(filter)
                            ? ''
                            : 'none';
                    }});
                }});

                Array.from(table.querySelectorAll('th')).forEach((th, index) => {{

                    let asc = true;

                    const arrow = document.createElement('span');
                    arrow.className = 'sort-arrow';

                    th.appendChild(arrow);

                    th.addEventListener('click', () => {{

                        const rows = Array.from(tbody.rows);

                        rows.sort((a, b) => {{

                            const valA = a.cells[index].innerText.toLowerCase();
                            const valB = b.cells[index].innerText.toLowerCase();

                            if (!isNaN(valA) && !isNaN(valB)) {{
                                return asc
                                    ? valA - valB
                                    : valB - valA;
                            }}

                            return asc
                                ? valA.localeCompare(valB)
                                : valB.localeCompare(valA);

                        }});

                        rows.forEach(row => tbody.appendChild(row));

                        Array.from(
                            table.querySelectorAll('.sort-arrow')
                        ).forEach(a => a.textContent = '');

                        arrow.textContent = asc ? '▲' : '▼';

                        asc = !asc;

                    }});
                }});

            </script>

        </body>

        </html>
        """

        return full_html