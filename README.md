# AI-Powered Landing Page Generation Crew

This project uses CrewAI to generate modern, responsive landing pages using only HTML, CSS, and JavaScript. It leverages multiple specialized AI agents to automate the creation of a complete, production-ready static website based on your website name and niche description.

---

## Overview

This project is an AI-powered system for generating complete, production-ready landing pages using only HTML, CSS, and JavaScript—no frameworks or build tools required. It leverages CrewAI agents, each with a realistic professional backstory and domain-specific goals, to collaboratively design, develop, and assemble all assets for a static website. The system is fully agent-driven, modular, and outputs a ready-to-host site with real, free-to-use images and proper attribution.

---

## Features
- **No Frameworks:** Pure HTML, CSS, and JavaScript output—no React, Node.js, or build tools.
- **Agent-Driven:** Four specialized agents (Project Setup Developer, Component Developer, JavaScript Developer, Asset Specialist) with rich, realistic goals and backstories.
- **Real Image Assets:** Asset Specialist finds and documents real, free-to-use images (Unsplash, Pexels, Pixabay) with attribution.
- **Configurable:** All API keys and configuration are handled via `.env` (never hardcoded).
- **Robust Output:** Modular directory structure for easy static hosting.
- **Comprehensive Documentation:** Full setup, usage, and agent details included.

---

## Setup

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd AI-Powered-Landing-Page-Generation-Crew
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure API keys:**
   - Create a `.env` file in the project root with the following content:
     ```env
     OPENROUTER_API_KEY=your_openrouter_api_key_here
     OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
     ```
   - Never commit your `.env` file or API keys to version control.

---

## Usage

To generate a new landing page, run:

```sh
python crew.py
```

- You will be prompted for the website name and a brief description.
- The system will generate all files in a new directory named `<website_name>_generated/`.
- All HTML, CSS, JS, and image assets (with attribution) will be included.

To test the generator and verify output:

```sh
python test_crew.py
```

---

## Agent Roles & Backstories

### 1. Project Setup Developer
- **Goal:** Architect the overall site structure, directory layout, and initial HTML boilerplate. Ensures modularity and maintainability.
- **Backstory:** A seasoned web architect with a passion for clean, scalable static sites. Expert in best practices for static web delivery.

### 2. Component Developer
- **Goal:** Designs and implements all HTML components (hero, features, testimonials, etc.) using semantic markup and accessibility best practices.
- **Backstory:** A creative front-end specialist with a keen eye for UX/UI and accessibility. Loves crafting beautiful, usable interfaces.

### 3. JavaScript Developer
- **Goal:** Adds all interactive features (animations, forms, navigation) using vanilla JavaScript. Ensures code is modular and unobtrusive.
- **Backstory:** A pragmatic JS engineer who believes in progressive enhancement and clean, maintainable code—no frameworks needed.

### 4. Asset Specialist
- **Goal:** Sources real, free-to-use images from Unsplash, Pexels, or Pixabay. Documents image URLs and attribution in a manifest file.
- **Backstory:** A resourceful digital asset manager with a knack for finding the perfect visuals and ensuring proper licensing and attribution.

---

## Output Structure

Each generated site is output to `<website_name>_generated/` with the following structure:

```
<website_name>_generated/
├── index.html
├── components/
│   └── ... (HTML partials)
├── styles/
│   └── main.css
├── js/
│   └── main.js
├── images/
│   └── ... (downloaded or linked images)
└── assets_manifest.json   # Image URLs and attribution
```

- All files are ready for static hosting (e.g., GitHub Pages, Netlify, Vercel).
- Attribution for all images is included in `assets_manifest.json`.

---

## Configuration

- All sensitive data (API keys, endpoints) must be set in `.env`.
- No secrets or configuration are hardcoded in the codebase.

---

## Testing

- Run `python test_crew.py` to verify the generator and output structure.
- The test script checks for file creation, content validity, and attribution.

---

## Contributing

Pull requests are welcome! Please ensure all new features:
- Use only HTML, CSS, and JavaScript (no frameworks or build tools).
- Keep all configuration externalized in `.env`.
- Maintain modular output structure and attribution requirements.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the agent-based workflow inspiration.
- [Unsplash](https://unsplash.com/), [Pexels](https://pexels.com/), and [Pixabay](https://pixabay.com/) for free image resources.

---

## Existing Features
- **No frameworks:** Pure HTML, CSS, and JS (no React, Node.js, or build tools)
- **Automated asset sourcing:** Finds and suggests free-to-use images from Unsplash, Pexels, or Pixabay
- **Modular code:** Generates semantic HTML components, modular CSS, and ES6+ JavaScript modules
- **Accessibility:** Ensures WCAG compliance and best practices
- **SEO optimized:** Adds meta tags, OpenGraph, and responsive images
- **Agent-based workflow:** Each agent specializes in a part of the process

## How It Works
1. **Project Setup Developer:** Creates the directory structure and base files (index.html, main.css, main.js)
2. **Asset Specialist:** Finds and documents relevant, free-to-use images for your website
3. **Component Developer:** Generates semantic HTML components and modular CSS for all landing page sections
4. **JavaScript Developer:** Implements all interactive features using vanilla JS modules

## Setup
1. Clone the repository
2. Create a `.env` file in the root directory with the following content:
   ```env
   OPENROUTER_API_KEY=<OPENROUTER_API_KEY>
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the generator:
   ```bash
   python test_crew.py
   ```

## Usage Example
```python
from crew import LandingPageCrew

website_name = "TechTrend"
niche_description = "A SaaS platform for tech startups offering AI-driven analytics"

crew = LandingPageCrew(website_name, niche_description)
result = crew.run()
```

## Output Structure
- `index.html` — Main landing page
- `components/` — HTML partials for hero, features, testimonials, pricing, contact
- `styles/` — main.css and component CSS files
- `js/` — main.js and JS modules for interactivity
- `images/` — Downloaded images and attribution file
- `SETUP.md` — Step-by-step setup instructions
- `README.md` — Full documentation

## Agent Roles
- **Project Setup Developer:** Sets up the folder structure and base files
- **Asset Specialist:** Finds and documents relevant images
- **Component Developer:** Builds HTML/CSS for all sections
- **JavaScript Developer:** Implements all JS features (carousel, form, navigation, etc.)

## License
This project is for educational and demonstration purposes. All generated images are sourced from free providers and must be used according to their respective licenses.

---
