import argparse
import time
import re
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

os.system("figlet meentestdorker ")

def extract_domains(links):
    domains = []
    for link in links:
        match = re.search(r"(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)", link)
        if match:
            domain = match.group(1)
            domains.append(domain)
    return domains

def filter_links(links):
    filtered_links = []
    for link in links:
        if "hackerone.com" in link or "bugcrowd.com" in link:
            continue
        try:
            response = requests.get(link)
            if "This program follows Bugcrowd's" in response.text or "Managed by HackerOne" in response.text:
                continue
            else:
                filtered_links.append(link)
        except:
            filtered_links.append(link)
    return filtered_links

def google_dorks_search(api_key, cse_id, dork_list):
    service = build("customsearch", "v1", developerKey=api_key)

    for dork in dork_list:
        print(f"Results for dork '{dork}':")
        for start in [1, 11, 21]:
            try:
                response = service.cse().list(q=dork, cx=cse_id, num=10, start=start).execute()
                links = [item["link"] for item in response.get("items", [])]
                domains = extract_domains(links)
                print(f"Number of links extracted: {len(links)}")
                if len(links) > 0:
                    search_choice = input("Do you want to check sites in hackerone and bugcrowd? (yes/no) ")
                    if search_choice.lower() == "yes":
                        for domain in domains:
                            for site in ["site:bugcrowd.com ", "site:hackerone.com "]:
                                search_query = site + domain
                                try:
                                    response = service.cse().list(q=search_query, cx=cse_id, num=10, start=1).execute()
                                    links += [item["link"] for item in response.get("items", [])]
                                except HttpError as e:
                                    print(f"Error searching query '{search_query}': {e}")
                        links = list(set(links))
                        filtered_links = filter_links(links)
                        if len(filtered_links) > 0:
                            print(f"Number of filtered links: {len(filtered_links)}")
                            for link in filtered_links:
                                print(link)
                        else:
                            print("No filtered links found")
                    else:
                        filtered_links = filter_links(links)
                        for link in filtered_links:
                            print(link)
                else:
                    print("No links found")
            except HttpError as e:
                print(f"Error searching dork '{dork}': {e}")
                break
        print("\n")
        time.sleep(10)

def main():
    parser = argparse.ArgumentParser(description="Google search tool based on the desired dorks")
    parser.add_argument('-k', '--api_key', required=True, help="API key for Google Custom Search API")
    parser.add_argument('-c', '--cse_id', required=True, help="Custom Search Engine ID")
    parser.add_argument('-d', '--dorks', nargs='+', required=True, help="List of dorks for searching")
    args = parser.parse_args()
    google_dorks_search(args.api_key, args.cse_id, args.dorks)
if __name__ == "__main__":
    main()
