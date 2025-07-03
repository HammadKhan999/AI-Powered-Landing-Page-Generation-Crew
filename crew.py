import os
import json
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from typing import Dict, List
import re
import string
from string import Template
from typing import Optional, Union

# Import regex

# Load environment variables
load_dotenv()

class LandingPageCrew:
    def __init__(self, website_name, niche_description):
        self.website_name = website_name
        self.niche_description = niche_description
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            openai_api_base=os.getenv('OPENROUTER_BASE_URL'),
            openai_api_key=os.getenv('OPENROUTER_API_KEY'),
            default_headers={"HTTP-Referer": "https://github.com/joaomdmoura/crewAI"}
        )
        self.generated_code = {}
        self.code_templates = {
            'html': Template('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title</title>
    <link rel="stylesheet" href="$css_path">
</head>
<body>
    $content
    <script src="$js_path"></script>
</body>
</html>'''),
            'css': Template(''':root {
    --primary-color: $primary_color;
    --secondary-color: $secondary_color;
    --accent-color: $accent_color;
}

body {
    font-family: $font_family;
    color: $text_color;
}'''),
            'js': Template('''// $module_name Module
(function() {
    'use strict';

    $content
})();''')
        }
        self.code_validators = {
            'html': self.validate_html,
            'css': self.validate_css,
            'js': self.validate_js
        }
        self.setup_instructions = []
        self.task_states = {
            "setup": {"completed": False, "retries": 0},
            "assets": {"completed": False, "retries": 0},
            "components": {"completed": False, "retries": 0},
            "js_modules": {"completed": False, "retries": 0}
        }
        self.processed_images = set()
        
    def validate_image_url(self, url: str) -> bool:
        """Validate if an image URL is real and accessible."""
        if not url or "..." in url or "placeholder" in url.lower():
            return False
        
        # Check if URL matches known patterns from free image providers
        valid_patterns = [
            r'https://images\.unsplash\.com/photo-\d+',
            r'https://images\.pexels\.com/photos/\d+',
            r'https://pixabay\.com/get/[\w-]+',
            r'https://source\.unsplash\.com/[\w-]+',
        ]
        
        return any(re.match(pattern, url) for pattern in valid_patterns)
        
    def update_task_state(self, task_type: str, success: bool, has_placeholders: bool = False):
        """Update task state and determine if retry is needed."""
        state = self.task_states[task_type]
        max_retries = 3
        
        if success and not has_placeholders:
            state["completed"] = True
            print(f"✓ {task_type} task completed successfully")
            return False  # No retry needed
            
        state["retries"] += 1
        if state["retries"] >= max_retries:
            print(f"⚠ {task_type} task failed after {max_retries} attempts")
            return False  # No more retries
            
        print(f"⚠ {task_type} task needs retry (Attempt {state['retries'] + 1})")
        return True  # Retry needed
        
    def create_agents(self):
        # Project Setup Agent
        setup_dev = Agent(
            role='Project Setup Developer',
            goal='''
            Create a clean, organized project structure for a static HTML website by:
            - Setting up proper directory structure for HTML, CSS, and JS files
            - Creating a development environment without external dependencies
            - Setting up asset organization for images and media
            - Establishing coding standards and best practices
            - Ensuring cross-browser compatibility
            ''',
            backstory='''
            A veteran web developer with 15 years of experience in pure HTML, CSS, and JavaScript.
            Expert in creating high-performance static websites without frameworks.
            Known for implementing sophisticated features using vanilla web technologies.
            Pioneer of the "Zero Dependencies" web development movement.
            Has built enterprise-level websites using only native web technologies.
            Regular speaker on web performance and maintainability.
            Author of "Pure Web Development: No Frameworks Needed".
            ''',
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )

        # Component Developer
        component_dev = Agent(
            role='Component Developer',
            goal='''
            Create visually stunning and accessible web components by:
            - Writing semantic HTML5 markup
            - Implementing modern CSS layouts and animations
            - Finding and optimizing relevant images for each section
            - Ensuring responsive design across all devices
            - Maintaining WCAG accessibility standards
            - Creating visual consistency throughout the site
            ''',
            backstory='''
            A creative technologist with 12 years of experience in UI/UX and visual design.
            Expert in crafting beautiful web experiences without frameworks.
            Specialized in finding and optimizing perfect images for websites.
            Created award-winning designs for major brands using pure HTML/CSS.
            Pioneer in responsive image techniques and lazy loading.
            Regular contributor to web design publications.
            Known for the "Visual-First Web Development" methodology.
            ''',
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )

        # JavaScript Developer
        js_dev = Agent(
            role='JavaScript Developer',
            goal='''
            Develop robust vanilla JavaScript solutions by:
            - Writing clean, modular JavaScript without frameworks
            - Implementing smooth animations and interactions
            - Creating responsive image loading mechanisms
            - Building efficient state management
            - Ensuring cross-browser compatibility
            - Optimizing performance and load times
            ''',
            backstory='''
            A JavaScript purist with 10 years of experience in vanilla JS development.
            Expert in creating complex functionality without external libraries.
            Developed popular vanilla JS utilities used by thousands of developers.
            Specialized in creating smooth animations and dynamic image galleries.
            Performance optimization expert focusing on Core Web Vitals.
            Regular speaker at JavaScript conferences.
            Author of "Pure JavaScript: Beyond Libraries and Frameworks".
            ''',
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )

        # Asset Specialist
        asset_dev = Agent(
            role='Asset Specialist',
            goal='''
            Source and optimize website assets by:
            - Finding relevant, free-to-use images for the website
            - Optimizing images for web performance
            - Creating image variants for different devices
            - Managing asset organization and naming
            - Ensuring proper image attribution
            - Documenting asset usage guidelines
            ''',
            backstory='''
            An asset optimization specialist with 8 years of experience in web media.
            Expert in finding and curating perfect images for websites.
            Specialized in image optimization and responsive image delivery.
            Created automated image optimization workflows used by major websites.
            Pioneer in modern image format adoption (WebP, AVIF).
            Regular speaker on web performance and image optimization.
            Maintains relationships with major free image providers.
            ''',
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )

        return setup_dev, component_dev, js_dev, asset_dev

    def store_generated_content(self, task_output, task_type):
        """Store generated content in the appropriate collection, parsing JSON robustly"""
        
        print(f"\nProcessing {task_type} task output...")
        
        # For empty or invalid output
        if not task_output:
            print(f"⚠ No content received for {task_type} task")
            return
            
        # Extract JSON from the output
        parsed_json = self.extract_json_from_string(task_output)
        if not parsed_json:
            print(f"⚠ Failed to parse JSON for {task_type} task")
            return

        try:
            # Handle each task type
            if task_type == "setup":
                if "directory_structure" in parsed_json:
                    self.generated_code["directory_structure"] = parsed_json["directory_structure"]
                    print("✓ Stored project structure")
                    
            elif task_type == "assets":
                if "images" in parsed_json:
                    image_data = parsed_json["images"]
                    valid_urls = 0
                    # Validate each image URL
                    for key, value in image_data.items():
                        if isinstance(value, dict):
                            if self.validate_image_url(value.get("url", "")):
                                valid_urls += 1
                        elif isinstance(value, list):
                            valid_urls += sum(1 for img in value if isinstance(img, dict) and self.validate_image_url(img.get("url", "")))
                    
                    if valid_urls > 0:
                        self.generated_code["images"] = image_data
                        print(f"✓ Stored {valid_urls} valid image assets")
                    else:
                        print("⚠ No valid image URLs found in assets")
                    
            elif task_type == "components":
                # Store HTML files
                html_files = {k: v for k, v in parsed_json.items() if k.endswith(('.html'))}
                if html_files:
                    self.generated_code["html_components"] = html_files
                    print(f"✓ Stored {len(html_files)} HTML components")
                
                # Store CSS files
                css_files = {k: v for k, v in parsed_json.items() if k.endswith(('.css'))}
                if css_files:
                    self.generated_code["css_components"] = css_files
                    print(f"✓ Stored {len(css_files)} CSS files")
                
                if not html_files and not css_files:
                    print("⚠ No HTML or CSS components found in output")
                    
            elif task_type == "js_modules":
                # Store JavaScript modules
                js_files = {k: v for k, v in parsed_json.items() if k.endswith(('.js'))}
                if js_files:
                    # Check for actual implementations
                    placeholder_count = sum(1 for content in js_files.values() 
                                         if any(ph in content for ph in ["// Implementation", "// TODO", "..."]))
                    
                    if placeholder_count == 0:
                        self.generated_code["js_modules"] = js_files
                        print(f"✓ Stored {len(js_files)} complete JavaScript modules")
                    else:
                        print(f"⚠ Found {placeholder_count} placeholder implementations in JavaScript modules")
                else:
                    print("⚠ No JavaScript modules found in output")
                
        except Exception as e:
            print(f"⚠ Error processing {task_type} task output: {str(e)}")
            print("Raw output:", task_output[:200] + "..." if len(str(task_output)) > 200 else task_output)
            
    def extract_json_from_string(self, s: str) -> Dict | None:
        """Extracts the first valid JSON object found within a string."""
        if not isinstance(s, str):
            return None
            
        def is_placeholder_content(content: str) -> bool:
            """Check if content is just a placeholder."""
            placeholder_patterns = [
                r'\.{3}',  # ...
                r'Implementation',
                r'Placeholder',
                r'Example',
                r'TODO',
                r'// *$',  # Empty comments
                r'Full implementation',
            ]
            return any(re.search(pattern, content, re.IGNORECASE) for pattern in placeholder_patterns)
        
        # Try to find JSON enclosed in ```json ... ``` or ``` ... ```
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', s, re.DOTALL | re.IGNORECASE)
        if match:  # Removed unnecessary parentheses
            json_str = match.group(1)
        else:
            # Fallback: find the first '{' and the last '}' 
            start = s.find('{')
            end = s.rfind('}')
            if start != -1 and end != -1 and start < end:  # Removed unnecessary parentheses
                json_str = s[start:end + 1]
            else:
                print(f"⚠ Could not find JSON structure in output.")
                return None

        try:
            # Try parsing directly first
            try:
                parsed = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Initial JSON parse failed: {e}. Attempting cleanup...")
                # Clean up common issues
                cleaned_json_str = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', '\\\\', json_str)
                cleaned_json_str = re.sub(r'(?<=":\s*")([^"\\]|\\.)*(?<!\\)\n', '\\n', cleaned_json_str)
                parsed = json.loads(cleaned_json_str)
            
            # Check for placeholder content in values
            for key, value in parsed.items():
                if isinstance(value, str) and is_placeholder_content(value):
                    print(f"⚠ Placeholder content detected in '{key}'. Requesting regeneration.")
                    return None
                elif isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, str) and is_placeholder_content(subvalue):
                            print(f"⚠ Placeholder content detected in '{key}.{subkey}'. Requesting regeneration.")
                            return None
            
            return parsed

        except Exception as e:
            print(f"⚠ Error parsing JSON: {str(e)}")
            return None

    def create_tasks(self, setup_dev, component_dev, js_dev, asset_dev):
        # Task 1: Generate Project Structure
        setup_task = Task(
            description=f"""
            Generate a COMPLETE, production-ready project structure for {self.website_name} ({self.niche_description}).
            Return a JSON object containing FULLY IMPLEMENTED files - NO PLACEHOLDERS.

            Required structure and implementations:

            1. index.html:
                Must include:
                - Complete HTML5 structure
                - Meta tags (charset, viewport, description)
                - SEO tags specific to {self.niche_description}
                - Stylesheet links
                - Module script tags
                - Basic layout structure
                Example:
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{self.website_name}</title>
                    ...
                </head>
                <body>...</body>
                </html>

            2. styles/main.css:
                Must include:
                - Modern CSS reset
                - Root variables for:
                    * Colors (primary, secondary, accent)
                    * Typography (font sizes, weights)
                    * Spacing scale
                    * Breakpoints
                - Base styles
                - Grid system
                - Utility classes
                Example:
                :root {{
                    --primary-color: #2563eb;
                    --spacing-unit: 0.25rem;
                    ...
                }}

            3. js/main.js:
                Must include:
                - Module imports
                - App initialization
                - Error handling
                Example:
                import {{ initComponents }} from './modules/index.js';
                document.addEventListener('DOMContentLoaded', () => {{
                    initComponents();
                }});

            Example output structure:
            {{
                "directory_structure": {{
                    "index.html": "<!DOCTYPE html>\\n<html lang=\\"en\\">...",
                    "styles/main.css": ":root {{ --primary-color: #2563eb; }}...",
                    "js/main.js": "import {{ initComponents }} from './modules/index.js';..."
                }}
            }}

            Requirements:
            - Write complete, working implementations
            - Include actual content specific to: {self.niche_description}
            - NO placeholder content
            - NO external dependencies
            """,
            expected_output="JSON object with complete project structure.",
            agent=setup_dev
        )

        # Task 2: Asset Collection and Optimization
        asset_task = Task(
            description=f"""
            Find and optimize relevant images for {self.website_name} ({self.niche_description}).
            Use free image sources like Unsplash, Pexels, or Pixabay.
            Return a JSON object containing:
            
            1. List of required images with exact URLs:
                - Hero section: Analytics dashboard or tech visualization
                - Features: Tech-related icons and illustrations
                - Team/testimonials: Professional team photos
                - Product: Dashboard screenshots or mockups
                - Logo/branding: Tech-focused logo ideas
            
            2. For each image provide:
                - Direct image URL (no placeholders)
                - Photographer/creator name and platform
                - License type (must be free to use)
                - Alt text for accessibility
                - Recommended dimensions and formats
                - Loading strategy (eager/lazy)
            
            Example structure:
            {{
                "images": {{
                    "hero": {{
                        "url": "https://images.unsplash.com/actual-image-id",
                        "thumbnail": "https://images.unsplash.com/actual-image-id?w=400",
                        "attribution": "John Doe on Unsplash",
                        "license": "Unsplash License",
                        "alt": "Modern analytics dashboard showing real-time data visualization",
                        "sizes": {{
                            "desktop": {{
                                "width": 1920,
                                "height": 1080,
                                "format": "webp"
                            }},
                            "tablet": {{
                                "width": 1024,
                                "height": 768,
                                "format": "webp"
                            }},
                            "mobile": {{
                                "width": 640,
                                "height": 480,
                                "format": "webp"
                            }}
                        }},
                        "loading": "eager"
                    }},
                    "features": [
                        {{
                            "url": "https://images.pexels.com/actual-image-id",
                            "thumbnail": "https://images.pexels.com/actual-image-id?w=200",
                            "attribution": "Jane Smith on Pexels",
                            "license": "Pexels License",
                            "alt": "AI-powered data analysis illustration",
                            "sizes": {{
                                "width": 800,
                                "height": 600,
                                "format": "webp"
                            }},
                            "loading": "lazy"
                        }}
                    ]
                }}
            }}

            Search for images that specifically match: {self.niche_description}
            Each image must have a direct, working URL - no placeholders allowed.
            Include at least 2-3 alternative images for each section.
            """,
            expected_output="JSON object with complete image assets information.",
            agent=asset_dev
        )

        # Task 3: Generate HTML and CSS Components
        component_task = Task(
            description=f"""
            Generate COMPLETE, production-ready HTML components with responsive CSS for {self.website_name}.
            Each component must work without any external dependencies.
            The components should match this niche: {self.niche_description}

            Required files and their COMPLETE implementations:

            1. index.html:
                Must include:
                - Doctype and UTF-8 encoding
                - Viewport meta tag
                - SEO meta tags (description, keywords)
                - OpenGraph tags
                - Favicon links
                - CSS imports in head
                - Deferred JS imports
                - Header with navigation
                - Main content sections
                - Footer with social links
                - Actual content (no lorem ipsum)

            2. components/:
                hero.html:
                    - Full viewport height hero section
                    - H1 heading with clear value proposition
                    - Subheading explaining benefits
                    - CTA button with clear action text
                    - Background image with gradient overlay
                    
                features.html:
                    - Grid/flex layout of 4-6 key features
                    - Icon or image for each feature
                    - Feature title and description
                    - CSS Grid or Flexbox layout
                    
                testimonials.html:
                    - Carousel/grid of 3-4 testimonials
                    - Customer photo, name, company
                    - Quote with specific feedback
                    - Navigation controls if carousel
                    
                pricing.html:
                    - 3-4 pricing tiers
                    - Most popular plan highlighted
                    - Feature comparison list
                    - Price with billing period
                    - CTA button for each plan
                    
                contact.html:
                    - Contact form with validation
                    - Name, email, message fields
                    - Submit button with loading state
                    - Success/error messages
                    - Company contact details

            3. styles/:
                main.css:
                    - CSS custom properties for colors
                    - Typography scale with rem units
                    - Responsive breakpoints
                    - Grid system with named areas
                    - Utility classes for spacing
                    - Dark/light mode support
                    
                components/*.css:
                    - BEM naming convention
                    - Mobile-first media queries
                    - Fluid typography
                    - CSS Grid/Flexbox layouts
                    - Smooth transitions
                    - Accessible focus states

            Example output structure (use this exact format):
            {{
                "index.html": "<!DOCTYPE html>\\n<html lang=\\"en\\">\\n<head>\\n<meta charset=\\"UTF-8\\">...",
                "components/hero.html": "<section class=\\"hero\\" aria-label=\\"Welcome\\">...",
                "components/features.html": "<section class=\\"features\\" aria-label=\\"Features\\">...",
                "styles/main.css": ":root {{ --primary-color: #007bff; }}...",
                "styles/components/hero.css": ".hero {{ min-height: 100vh; }}..."
            }}

            Requirements:
            - Use semantic HTML5 elements
            - Include WAI-ARIA attributes
            - Add proper alt text for images
            - Use native lazy loading
            - Include actual content specific to: {self.niche_description}
            - NO placeholder content or lorem ipsum
            - NO external dependencies
            """,
            expected_output="JSON object with complete HTML/CSS implementations.",
            agent=component_dev
        )

        # Task 4: Generate JavaScript Functionality
        js_task = Task(
            description=f"""
            Create COMPLETE, production-ready vanilla JavaScript modules for {self.website_name}.
            No external dependencies or placeholders allowed.
            The code should implement functionality specific to: {self.niche_description}

            Required modules and their full implementations:

            1. js/main.js:
                Must include:
                - ES6 module imports
                - DOMContentLoaded listener
                - Feature detection
                - Error handling setup
                - Analytics initialization
                - Performance monitoring

            2. js/modules/imageLoader.js:
                Must implement:
                - Intersection Observer for lazy loading
                - Progressive image loading
                - Fallback for older browsers
                - Error handling for failed loads
                - WebP support detection
                - Responsive image switching
                Example: 
                export class ImageLoader {{
                    constructor() {{
                        this.observer = new IntersectionObserver(...);
                    }}
                    init() {{
                        // Full implementation
                    }}
                }}

            3. js/modules/carousel.js:
                Must implement:
                - Touch-enabled slider
                - Keyboard navigation
                - A11y announcements
                - Auto-play with pause
                - Progress indicators
                - Smooth animations

            4. js/modules/navigation.js:
                Must implement:
                - Mobile menu toggle
                - Smooth scroll to sections
                - Active section highlighting
                - Scroll progress indicator
                - Sticky header logic
                - Keyboard navigation

            5. js/modules/form.js:
                Must implement:
                - Real-time validation
                - Custom error messages
                - AJAX form submission
                - Loading states
                - Success/error handling
                - Input masking

            6. js/modules/animations.js:
                Must implement:
                - Scroll-triggered animations
                - Intersection Observer usage
                - Performance throttling
                - Reduced motion support
                - CSS class toggling
                - Animation sequences

            7. js/utils/:
                analytics.js:
                    - Page view tracking
                    - Event tracking
                    - Performance monitoring
                validation.js:
                    - Email validation
                    - Input sanitization
                    - Error message handling
                api.js:
                    - Fetch wrapper
                    - Error handling
                    - Retry logic

            Example structure (use this exact format):
            {{
                "js/main.js": "import {{ ImageLoader }} from './modules/imageLoader.js';\\n\\ndocument.addEventListener('DOMContentLoaded', () => {{\\n  // Full implementation\\n}});",
                "js/modules/imageLoader.js": "export class ImageLoader {{\\n  constructor() {{\\n    // Full implementation\\n  }}\\n}}",
                "js/modules/carousel.js": "export class Carousel {{\\n  // Full implementation\\n}}",
                "js/utils/analytics.js": "export const trackEvent = (category, action, label) => {{\\n  // Full implementation\\n}}"
            }}

            Requirements:
            - Use ES6+ features (classes, modules, async/await)
            - Include error handling for all async operations
            - Add performance monitoring
            - Ensure cross-browser compatibility
            - Include JSDoc comments
            - NO placeholder implementations
            - NO external dependencies
            """,
            expected_output="JSON object with complete JavaScript implementations.",
            agent=js_dev
        )

        return [setup_task, asset_task, component_task, js_task]

    def compile_output(self, task_results): # Changed parameter name for clarity
        """Compile the generated code and instructions into a structured format"""
        # Documentation is now stored in generated_code, retrieve it
        documentation_content = self.generated_code.get("documentation", "Documentation generation failed.")
        return {
            'project_name': self.website_name,
            'description': self.niche_description,
            'setup_instructions': self.setup_instructions, # Basic setup steps
            'generated_code': self.generated_code, # Contains config, components, types
            'documentation': documentation_content # Full markdown docs
        }

    def run(self):
        try:
            # Create agents
            setup_dev, component_dev, js_dev, asset_dev = self.create_agents()

            # Create tasks
            tasks = self.create_tasks(setup_dev, component_dev, js_dev, asset_dev)

            # Create crew
            crew = Crew(
                agents=[setup_dev, component_dev, js_dev, asset_dev],
                tasks=tasks,
                verbose=2
            )

            print("\nStarting landing page generation for:", self.website_name)
            print("Description:", self.niche_description)

            # Let the agents do their work through CrewAI
            try:
                results = crew.kickoff()
                
                # Process results based on task order
                task_types = ["setup", "assets", "components", "js_modules"]
                for i, task_type in enumerate(task_types):
                    result = results[i] if isinstance(results, list) and i < len(results) else None
                    if result:
                        print(f"✓ {task_type} task completed by agent")
                        self.store_generated_content(result, task_type)
                    else:
                        print(f"⚠ {task_type} task returned no result")

            except Exception as e:
                print(f"⚠ Error during task execution: {str(e)}")
                return None

            # Compile final output
            output = self.compile_output(results if isinstance(results, list) else [results])

            # Write files
            print("\nWriting generated files...")
            self.write_output_to_files(output)

            print(f"\n✓ Landing page generation completed for {self.website_name}")
            return output

        except Exception as e:
            print(f"\n⚠ Error during landing page generation: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def write_output_to_files(self, output):
        """Write the generated code and documentation to files"""
        output_dir = self.website_name.lower() + "_generated"
        os.makedirs(output_dir, exist_ok=True)
        print("\nAttempting to write generated files to: " + output_dir)

        try:
            # Write setup instructions
            setup_md_path = os.path.join(output_dir, "SETUP.md")
            setup_instructions = [
                "# Project Setup Instructions",
                "",
                "1. Set up project directories:",
                f"   - Create directory: {self.website_name.lower()}",
                "   - Create subdirectories: styles/, js/, images/, components/",
                "",
                "2. Copy website files:",
                "   - Place HTML files in the root directory",
                "   - Copy CSS files to styles/",
                "   - Copy JavaScript files to js/",
                "",
                "3. Set up images:",
                "   - Download the images from URLs in images/images.json",
                "   - Place them in the images/ directory",
                "   - Update HTML files with correct image paths",
                "",
                "4. Start development:",
                "   - Open index.html in a web browser",
                "   - Test all components and features",
                "   - Verify responsive design",
                "   - Check image loading performance"
            ]
            with open(setup_md_path, "w", encoding='utf-8') as f:
                f.write("\n".join(setup_instructions))
            print("  - Wrote " + setup_md_path)

            generated_code = output.get("generated_code", {})

            # Write project structure files
            if "directory_structure" in generated_code:
                for filepath, content in generated_code["directory_structure"].items():
                    full_path = os.path.join(output_dir, filepath)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    try:
                        with open(full_path, "w", encoding='utf-8') as f:
                            f.write(content if isinstance(content, str) else str(content))
                        print(f"  ✓ Created file: {filepath}")
                    except Exception as e:
                        print(f"  ⚠ Error writing file {filepath}: {str(e)}")

            # Write image assets information
            if "images" in generated_code:
                images_dir = os.path.join(output_dir, "images")
                os.makedirs(images_dir, exist_ok=True)
                
                # Write image metadata
                images_json_path = os.path.join(images_dir, "images.json")
                try:
                    with open(images_json_path, "w", encoding='utf-8') as f:
                        json.dump(generated_code["images"], f, indent=2)
                    print("  ✓ Created image assets index: images.json")
                    
                    # Create image attribution file
                    attribution_md = ["# Image Attributions", ""]
                    for section, images in generated_code["images"].items():
                        if isinstance(images, dict):
                            attribution_md.extend([
                                f"## {section.title()}",
                                f"- Source: {images.get('url', 'Unknown')}",
                                f"- Attribution: {images.get('attribution', 'Unknown')}",
                                f"- License: {images.get('license', 'Unknown')}",
                                ""
                            ])
                        elif isinstance(images, list):
                            attribution_md.append(f"## {section.title()}")
                            for img in images:
                                attribution_md.extend([
                                    f"- Source: {img.get('url', 'Unknown')}",
                                    f"  Attribution: {img.get('attribution', 'Unknown')}",
                                    f"  License: {img.get('license', 'Unknown')}",
                                    ""
                                ])
                    
                    attribution_path = os.path.join(images_dir, "ATTRIBUTION.md")
                    with open(attribution_path, "w", encoding='utf-8') as f:
                        f.write("\n".join(attribution_md))
                    print("  ✓ Created image attribution file: images/ATTRIBUTION.md")
                    
                except Exception as e:
                    print(f"  ⚠ Error writing image assets: {str(e)}")

            # Write HTML components
            if "html_components" in generated_code:
                components_dir = os.path.join(output_dir, "components")
                os.makedirs(components_dir, exist_ok=True)
                for name, content in generated_code["html_components"].items():
                    filepath = os.path.join(components_dir, name)
                    try:
                        with open(filepath, "w", encoding='utf-8') as f:
                            f.write(content)
                        print(f"  ✓ Created component: {name}")
                    except Exception as e:
                        print(f"  ⚠ Error writing component {name}: {str(e)}")

            # Write CSS files
            if "css_components" in generated_code:
                styles_dir = os.path.join(output_dir, "styles")
                os.makedirs(styles_dir, exist_ok=True)
                for name, content in generated_code["css_components"].items():
                    filepath = os.path.join(styles_dir, name)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    try:
                        with open(filepath, "w", encoding='utf-8') as f:
                            f.write(content)
                        print(f"  ✓ Created CSS: {name}")
                    except Exception as e:
                        print(f"  ⚠ Error writing CSS {name}: {str(e)}")

            # Write JavaScript modules
            if "js_modules" in generated_code:
                js_dir = os.path.join(output_dir, "js")
                os.makedirs(js_dir, exist_ok=True)
                for name, content in generated_code["js_modules"].items():
                    filepath = os.path.join(js_dir, name)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    try:
                        with open(filepath, "w", encoding='utf-8') as f:
                            f.write(content)
                        print(f"  ✓ Created JS module: {name}")
                    except Exception as e:
                        print(f"  ⚠ Error writing JS module {name}: {str(e)}")

            # Print summary
            print("\nFile generation summary:")
            print(f"  Project root: {output_dir}")
            print("  Structure:")
            print("    ├── index.html")
            print("    ├── components/")
            print("    │   ├── hero.html")
            print("    │   ├── features.html")
            print("    │   ├── testimonials.html")
            print("    │   └── contact.html")
            print("    ├── styles/")
            print("    │   ├── main.css")
            print("    │   └── components/")
            print("    ├── js/")
            print("    │   ├── main.js")
            print("    │   └── modules/")
            print("    └── images/")
            print("        ├── images.json")
            print("        └── ATTRIBUTION.md")
            print("\n✓ File generation completed successfully")

        except Exception as e:
            print("Error during file writing: " + str(e))
            import traceback
            traceback.print_exc()

if __name__ == "__main__": 
    # Example usage
    website_name = "TechTrend"
    niche_description = "A SaaS platform for tech startups offering AI-driven analytics"
    
    crew = LandingPageCrew(website_name, niche_description)
    result = crew.run()
    print(result)