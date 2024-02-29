import pandas as pd
import requests
import io
import os
    
def getTop4Establishment(country, stateAbbr, naicsLevel, year, state, outputFolder):
    csv_url = f"https://model.earth/community-data/industries/naics/{country}/counties/{stateAbbr}/{country}-{stateAbbr}-census-naics{str(naicsLevel)}-{str(year)}.csv"
    industry_url = "https://model.earth/community-data/us/id_lists/industry_id_list.csv"
    #df_input = pd.read_csv(csv_url)
    #df_industry = pd.read_csv(industry_url)
    df_input = pd.read_csv(io.StringIO(requests.get(csv_url).content.decode('utf-8')))
    df_industry = pd.read_csv(io.StringIO(requests.get(industry_url).content.decode('utf-8')))

    df_sorted = df_input.sort_values(by="Establishments", ascending=False)
    df_extracted = df_sorted.iloc[:4, :].reset_index(drop=True)
    #print(df_extracted)

    df_merged = pd.merge(df_extracted, df_industry, left_on='Naics', right_on='relevant_naics', how='left')
    df_merged.drop(['relevant_naics', "Unnamed: 0"], axis=1, inplace=True)
    df_merged.rename(columns={"industry_detail": "Industry"}, inplace=True)
    output_name = f"{stateAbbr}-prompts-{str(year)}.csv"
    
    df_merged['Prompt'] = None
    
    def getPrompt(industry, state, year):

        prompts = [
            f"A honey bee is near a location that provides {industry} in {state} in {str(year)}.",
            f"A street under a tree canopy near a location that provides {industry} in {state} in {str(year)}.",
            f"An innovation that creates jobs in {industry} in {state} in {str(year)}.",
            f"An innovation that reduces poverty in {industry} in {state} in {str(year)}."
        ]

        return prompts
    
    prompts_list = [getPrompt(df_merged["Industry"][i], state, year) for i in range(len(df_merged))]
    df_merged["Prompt"] = prompts_list
        

    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    print(df_merged)

    df_merged.to_csv(os.path.join(outputFolder, output_name),index=False)
    
getTop4Establishment("US", "ME", 4, 2021, "Maine", "prompts/industries")
getTop4Establishment("US", "OR", 4, 2021, "Oregon", "prompts/industries")