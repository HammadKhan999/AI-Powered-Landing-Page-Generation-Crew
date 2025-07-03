from crew import LandingPageCrew

def test_landing_page_generation():
    # Test case 1: Tech startup
    website_name = "TechTrend"
    niche_description = "A SaaS platform for tech startups offering AI-driven analytics"
    
    print("=== Testing Landing Page Generation ===")
    print(f"Website: {website_name}")
    print(f"Niche: {niche_description}\n")
    
    # Create crew and run generation
    crew = LandingPageCrew(website_name, niche_description)
    result = crew.run()
    
    # Check results
    if result:
        print("\n=== Generation Results ===")
        print(f"Project Name: {result['project_name']}")
        print(f"Description: {result['description']}")
        print("\nGenerated Files:")
        if 'generated_code' in result:
            for category in result['generated_code']:
                if isinstance(result['generated_code'][category], dict):
                    print(f"- {category}: {len(result['generated_code'][category])} files")
    else:
        print("\n❌ Landing page generation failed")

if __name__ == "__main__":
    test_landing_page_generation()