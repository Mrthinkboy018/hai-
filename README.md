# Scrap Shop Places Automation

This project collects scrap shop business details using the **Google Places API** (Text Search + Place Details), exports them into an Excel file, and generates a simple responsive website for each shop. It uses **requests**, **pandas**, and **openpyxl**.

## Features

- Google Places **Text Search** for discovery
- Google Places **Place Details** for phone/website/rating
- Excel export (`.xlsx`) with the required columns
- One responsive HTML website per shop

## Setup

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Add your Google Places API key

Set an environment variable (recommended):

```bash
export GOOGLE_PLACES_API_KEY="YOUR_API_KEY_HERE"
```

You can also pass `--api-key` directly when running the script.

### 3) Run the script

```bash
python places_automation.py \
  --keyword "scrap shop" \
  --location "Austin, TX" \
  --max-pages 3
```

**Example with explicit API key:**

```bash
python places_automation.py \
  --keyword "scrap shop" \
  --location "Austin, TX" \
  --api-key "YOUR_API_KEY_HERE"
```

## Output

### Excel file

- Filename format: `scrap_shops_<location>.xlsx`
- Example: `scrap_shops_austin_tx.xlsx`
- Columns:

| Name | Address | Phone | Website | Rating | Latitude | Longitude | Place ID |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Example Scrap Co | 123 Main St, Austin, TX | +1 555-0100 | https://example.com | 4.4 | 30.2672 | -97.7431 | ChIJ123... |

### Website generator

- Output directory: `websites/`
- One folder per shop: `websites/<shop_name>/index.html`

#### Sample generated HTML (snippet)

```html
<header>
  <h1>Example Scrap Co</h1>
</header>
<main>
  <section class="info">
    <div>
      <h2>Address</h2>
      <p>123 Main St, Austin, TX</p>
    </div>
    <div>
      <h2>Phone</h2>
      <p>+1 555-0100</p>
      <a class="cta" href="https://wa.me/15550100" target="_blank">WhatsApp</a>
    </div>
  </section>
  <section>
    <h2>Location</h2>
    <iframe src="https://www.google.com/maps?q=30.2672,-97.7431&z=15&output=embed"></iframe>
  </section>
  <section>
    <h2>Contact Us</h2>
    <form>
      <input type="text" name="name" placeholder="Your Name" required />
      <input type="email" name="email" placeholder="Email Address" required />
      <textarea name="message" rows="4" placeholder="How can we help?" required></textarea>
      <button type="submit">Send Message</button>
    </form>
  </section>
</main>
```

## Notes

- The script uses the Google Places API only (no scraping or browser automation).
- Missing phone numbers or websites are labeled as `Not available`.
- The WhatsApp button is disabled if a phone number is missing.
