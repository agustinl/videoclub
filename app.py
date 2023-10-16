from flask import Flask, render_template, request, Response
from dotenv import load_dotenv

app = Flask(__name__)

import os
import requests
import json

load_dotenv()

OMDB_API = os.getenv('OMDB_API')
KEY = os.getenv('KEY')

with open('assets/series.json', encoding='utf-8') as f:
    data = json.load(f)
    data.sort(key=lambda x: x['id'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/series', methods=['GET'])
def get_series():
    order = request.args.get('order')
    order_reverse = True
    
    if order == None:
        order = 'last'
        
    if order == 'first':
        order_reverse = False
     
    html_content = ""
    data.sort(key=lambda x: x['id'], reverse=order_reverse)
    
    html_content += f"""
        <div class="flex justify-between items-center flex-wrap gap-4">
        	<h3 class="text-md font-semibold mt-4 mb-2">{len(data)} series</h3>
          	<select name="order" hx-get="/series" hx-target="#list" hx-swap="innerHTML" hx-indicator="#indicator" class="text-sm text-black font-semibold">
				<option value="last" {"selected" if order == "last" else ""}>last views</option>
				<option value="first" {"selected" if order == "first" else ""}>first views</option>
			</select>
        </div>
    """

    for item in data:
        html_content += f"""
			<article class="p-4 mb-4 rounded-md border border-gray-100 flex gap-4">
                <img src="{item['Poster']}" class="h-[120px] w-auto sm:w-2/12 sm:h-auto rounded-md" />
                <div class="flex justify-between flex-col">
                    <div>
                        <h2 class="text-md font-semibold mb-2">{item['Title']}</h2>
                        <p class="text-sm text-gray-400 mb-4">{item['Plot']}</p>
                    </div>
                    <div class="text-sm text-black font-semibold flex gap-4 flex-wrap">
                        <p class="flex items-center gap-1">
                           <svg viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" width="17" height="17"><path d="M7.953 3.788a.5.5 0 00-.906 0L6.08 5.85l-2.154.33a.5.5 0 00-.283.843l1.574 1.613-.373 2.284a.5.5 0 00.736.518l1.92-1.063 1.921 1.063a.5.5 0 00.736-.519l-.373-2.283 1.574-1.613a.5.5 0 00-.283-.844L8.921 5.85l-.968-2.062z" fill="currentColor" class="fill-yellow-500"></path></svg>
                            {item['imdbRating']} ({item['imdbVotes']} votes)
                        </p>
                        <p>{item['totalSeasons']} seasons</p>
                        <p>{item['Year']}</p>
                    </div>
                </div>
        </article>
        """

    return html_content

@app.route("/search", methods=['POST'])
def get_serie():
    
	query = request.form.get('search_input')
	html_content = ""

	if len(query) == 0:
		return html_content

	response = requests.get(f"http://www.omdbapi.com/?apikey={OMDB_API}&t=${query}&type=series")
    
	if response:
		item = response.json()
		data.sort(key=lambda x: x['id'])
		
		if item.get('Title') == None:
			html_content = f"""
            <article class="p-4 mb-4 rounded-md border border-red-600 fadeOut">
                <h2 class="text-sm font-semibold">{item['Error']}</h2>
            </article>
            """
		else:
			values_to_send = {					
				'id': data[-1]['id'] + 1,
				'Title': item['Title'],
				'Year': item['Year'],
				'Rated': item['Rated'],
				'Released': item['Released'],
				'Runtime': item['Runtime'],
				'Genre': item['Genre'],
				'Plot': item['Plot'].replace("'", ""),
				'Language': item['Language'],
				'Country': item['Country'],
				'Awards': item['Awards'],
				'Poster': item['Poster'],
				'imdbRating': item['imdbRating'],
				'imdbVotes': item['imdbVotes'],
				'imdbID': item['imdbID'],
				'totalSeasons': item['totalSeasons'],
			}
			values_to_send = json.dumps(values_to_send)
			html_content = f"""
                <article class="p-4 mb-4 rounded-md border border-green-600 flex gap-4">
                    <img src="{item['Poster']}" class="h-[120px] w-auto sm:w-2/12 sm:h-auto rounded-md" />
                    <div class="flex justify-between flex-col">
                        <div>
                            <h2 class="text-md font-semibold mb-2">{item['Title']}</h2>
                            <p class="text-sm text-gray-400 mb-4">{item['Plot']}</p>
                        </div>
                        <div class="flex justify-between items-end w-full flex-wrap gap-4">
                            <div class="text-sm text-black font-semibold flex gap-4 flex-wrap">
                                <p class="flex items-center gap-1">
                                    <svg viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" width="17" height="17"><path d="M7.953 3.788a.5.5 0 00-.906 0L6.08 5.85l-2.154.33a.5.5 0 00-.283.843l1.574 1.613-.373 2.284a.5.5 0 00.736.518l1.92-1.063 1.921 1.063a.5.5 0 00.736-.519l-.373-2.283 1.574-1.613a.5.5 0 00-.283-.844L8.921 5.85l-.968-2.062z" fill="currentColor" class="fill-yellow-500"></path></svg>
                                    {item['imdbRating']} ({item['imdbVotes']} votes)
                                </p>
                                <p>{item['totalSeasons']} seasons</p>
                                <p>{item['Year']}</p>
                            </div>
                            <button class="bg-black text-white px-6 py-2 text-xs font-semibold rounded-md" type="button" id="add-button" hx-post="/add" hx-trigger="click" hx-indicator="#indicator" hx-vals='{values_to_send}' hx-swap="innerHTML" hx-target="#response" hx-prompt="Enter key">Add</button>
                        </div>
                    </div>
            </article>
            """
		return html_content
	else:
		html_content = f""" 
            <article class="p-4 mb-4 rounded-md border border-red-600 fadeOut">
                <h2 class="text-sm font-semibold">Serie not found</h2>
            </article>
            """

	return html_content

@app.route("/add", methods=['POST'])
def add_serie():
	key = request.headers.get('Hx-Prompt')
    
	if key == KEY:
		html_content = ""
		new_serie = request.form.to_dict()    
		new_serie.update({ 'id': int(request.form['id'])})
		
		data.append(new_serie)
		
		with open('assets/series.json', 'w') as f:
			json.dump(data, f)
			html_content = f""" 
				<article class="p-4 mb-4 rounded-md border border-green-600 fadeOut">
					<h2 class="text-sm font-semibold">Serie added</h2>
				</article>
				"""
				
		resp = Response(html_content)
		resp.headers['HX-Trigger'] = 'newSerieAdded'
				
		return resp
	else:
		html_content = f""" 
			<article class="p-4 mb-4 rounded-md border border-red-600">
				<h2 class="text-sm font-semibold">Wrong key</h2>
    			<p class="text-sm text-gray-400">This is a personal list, so series cannot be included without the key.</p>
			</article>
			"""
		return html_content

@app.route('/series_json', methods=['GET'])
def get_series_in_json():
    data.sort(key=lambda x: x['id'])
    
    return data