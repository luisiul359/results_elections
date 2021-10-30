import requests
import pandas as pd

from tqdm import tqdm


# same as Portugal
ROOT_KEY = "LOCAL-500000"


def get_data(path):
  """ Load data from a certain endpoint """
  
  try:
    payload = requests.get(
      path,
      # fake, but wihtout it the request is rejected
      headers={'User-Agent': 'Mozilla/5.0'}
    )
    assert payload.status_code == 200

    return payload.json()
  except Exception as e:
    print(path)
    raise e


def get_results(elections_name, path_children, path_results):
  """
  All data from https://www.eleicoes.mai.gov.pt/ have same schema, thus we can use the same code for all portuguese elections

  Paths must be a string format with a named argument called key.

  Keyword arguments:
  elections_name -- name of the elections being processed
  path_children -- path to geographical regions below current location, e.g., all county under a district
  path_results -- path to collect all results of a certain region, e.g., district, county, or parish
  """

  districts = get_data(path_children.format(key=ROOT_KEY))

  results = []
  for district in tqdm(districts, f"Processing {elections_name}"):
    district_name = district["name"]
    district_key = district["territoryKey"]

    counties = get_data(path_children.format(key=district_key))

    for county in tqdm(counties):
      county_name = county["name"]
      county_key = county["territoryKey"]

      parishes = get_data(path_children.format(key=county_key))

      for parish in parishes:
        parish_nome = parish["name"]
        parish_key = parish["territoryKey"]

        parish_resuls = get_data(path_results.format(key=parish_key))

        d = {
          "distrito": district_name,
          "concelho": county_name,
          "freguesia": parish_nome,
          "votos_brancos": parish_resuls.get("currentResults", {}).get("blankVotes", -1),
          "votos_nulos": parish_resuls.get("currentResults", {}).get("nullVotes", -1),
          "total_eleitores": parish_resuls.get("currentResults", {}).get("subscribedVoters", -1),
          "total_eleitores_votantes": parish_resuls.get("currentResults", {}).get("totalVoters", -1)
        }

        for results_party in parish_resuls.get("currentResults", {}).get("resultsParty", []):
          party_name = results_party.get("acronym", "")
          party_result = results_party.get("votes", -1)

          if party_name:
            d[party_name] = party_result

        results.append(d)

  # be sure we do not have spaces
  filename = elections_name.lower().replace(" ", "_")

  pd.DataFrame(results).to_excel(f"results_{filename}.xlsx")

  print("Done")


if __name__ == "__main__":

  get_results(
    "Legislativas 2019",
    "https://www.eleicoes.mai.gov.pt/legislativas2019/static-data/territory-children/TERRITORY-CHILDREN-{key}.json",
    "https://www.eleicoes.mai.gov.pt/legislativas2019/static-data/territory-results/TERRITORY-RESULTS-{key}-AR.json"
  )

  get_results(
    "Europeias 2019",
    "https://www.eleicoes.mai.gov.pt/europeias2019/static-data/territory-children/TERRITORY-CHILDREN-{key}.json",
    "https://www.eleicoes.mai.gov.pt/europeias2019/static-data/territory-results/TERRITORY-RESULTS-{key}-EUR.json"
  )

  get_results(
    "Presidenciais 2021",
    "https://www.eleicoes.mai.gov.pt/presidenciais2021/assets/static/territory-children/territory-children-{key}.json",
    "https://www.eleicoes.mai.gov.pt/presidenciais2021/assets/static/territory-results/territory-results-{key}-PR.json"
  )

  for type in "CM AM AF".split():
    get_results(
      f"Autarquicas 2021 {type}",
      "https://www.autarquicas2021.mai.gov.pt/frontend/data/TerritoryChildren?territoryKey={key}",
      "https://www.autarquicas2021.mai.gov.pt/frontend/data/TerritoryResults?territoryKey={key}&electionId=" + type
    )
