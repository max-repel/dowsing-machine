<!-- ABOUT THE PROJECT -->
## dowsing-machine
<a id="readme-top"></a>

<img alt="image" src="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/413c5bb0-713b-498a-a17a-c98cce504500/df5rzgo-69631ed5-30fb-4285-b843-d5277e528ae3.png/v1/fill/w_1032,h_774/item_finder__dowsing_machine__by_hiimzoxo_df5rzgo-pre.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9OTYwIiwicGF0aCI6Ii9mLzQxM2M1YmIwLTcxM2ItNDk4YS1hMTdhLWM5OGNjZTUwNDUwMC9kZjVyemdvLTY5NjMxZWQ1LTMwZmItNDI4NS1iODQzLWQ1Mjc3ZTUyOGFlMy5wbmciLCJ3aWR0aCI6Ijw9MTI4MCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.fvGYZM4C9ZhXrA5o9ubZof2EcO_7Bn3it-gnpdcfM5M" />

dowsing-machine is a normalized and consistent relational database with game data from most previous pokemon games as well 10+ years of Smogon's battle data for every metagame. Relations between the two data sources are connected and normalized mainly based on the star schema paradigm. Data is stored in PostgreSQL.

dowsing-machine is also a tool for my own personal curiosity. As the name suggests, it uncovers "invisible" insights within the data in order to answer any questions regarding previous games or the history of Smogon's battling scene. The database provides a good foundation of data to perform complex analysis with several ML algortihms like regression, clustering, PCA, etc.

Some example questions that I currently have:

- In Pokemon Emerald, can I catch a pokemon that can learn Cut in Petalburg Woods?
- Are there any purple pokemon I can catch in Route 3 of Pokemon Black/White?
- What is the median speed of all rock type pokemon?
- What may have caused Registeel's usage rate to go up by 5% in Gen 3 OU?
- What is a highly underrated but viable pokemon within any Gen 9 format?
- How much of an impact does a pokemon's ability to learn the move rapid spin affect it's usage percentage?
- Which held item had the highest spike in popularity between the years 2020 and 2021?
- For any of WolfeyVGC's "Top 10 [type] pokemon of all time video", how accurately am I able to predict his top 10?
- And many more...


These are the questions that I hope to be able to answer and visualize with this tool.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ROADMAP -->
## Roadmap

- [ ] Clean and normalize all data from PokeAPI and Smogon and load into Postgres.
  - [ ] Figure out how to associate pokemon with generation introduced, as this data is currently not in PokeAPI. <-- Currently here
  - [ ] Efficiently deal with all of the small data inconsistencies in Smogon's data that piled up over the past decade like inconsistent naming and name changes especially within metagame formats. <-- Currently here
  - [ ] Optimize for faster loading. It is currently not as fast as I would like it to be. <-- Currently here
- [ ] Dynamic dashboarding for each pokemon and its entire history of competitive usage based on Smogon data.
- [ ] Uncover insights with ML algs (Inference/Predictions)
- [ ] Support for lightweight LLM trained on the entire dataset to generate SQL queries. (?)
- [ ] Orchestrate new Smogon data each month using Airflow.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


Visuals coming soonTM.
