# Pathfinder

This program performs the computation of the travelling salesman problem on a given set of GPS points. So far, the computation is implemented using brute force and nearest neighbour method.

## Usage
1. Obtain an API key for the openrouteservice API. You can generate your own api key at https://openrouteservice.org/.
2. Run the app in Docker: `docker compose up --build`
3. Find out the app IP address: `docker inspect pathfinder-web-1 | grep IP`
4. Using tool like Postman, make a `POST` request to the app's compute endpoint, e. g. `172.24.0.3:5000/compute/`.
5. In the body of the request, add:
   - key `file`, value `<the input gpx file>`
   - key `method_type`, value `brute_force` or `nearest_neighbour`
   - key `api_key`, value `<your openrouteservice API key>`
6. In the response, you will obtain the task_id of your job.
7. To obtain the results, make a `GET` request to the app's results endpoint, e. g. `172.24.0.3:5000/result/9308ce2f-b1a9/`.

## Notes
- This program uses the openrouteservice API. You have to generate an API key in order to make this program work.
- The output of the openrouteservice API is only pure route. The waypoints are added manually from the input file.

## Background

Whenever I traveled to a city, I always found a few places I wanted to visit. Then I needed to find the optimal route that I could take to visit all those places. That's how the idea for this project was born.

I found an API to calculate distances between GPS points. Then I implemented a simple solution using brute force method. After that, I decided to add a GUI to practice working with the PyQt5 library. Then I added a graphical representation of the calculation and the resulting path. This was followed by an extension to perform the shortest path calculation using the nearest neighbor method, which was also the first solution method I thought of.

The next steps are, for example, to implement other methods to solve the TSP or to represent the solution directly in the integrated map.
