// backend/scraper.js
const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const { LRUCache } = require('lru-cache');
const fetch = require('node-fetch'); // ✅ required if using Node < 18

const cache = new LRUCache({ max: 100, ttl: 1000 * 60 * 5 });

async function scrapeMovies() {
  if (cache.has('movies')) {return cache.get('movies');}

  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  const targetUrl = 'https://example-torrent-site.com/movies';
  await page.goto(targetUrl, { waitUntil: 'domcontentloaded' });

  const html = await page.content();
  const $ = cheerio.load(html);
  let movies = [];

  $('.movie-item').each((i, elem) => {
    const title = $(elem).find('.movie-title').text().trim();
    const link = $(elem).find('a').attr('href');
    movies.push({ id: `${i}`, title, link });
  });

  await browser.close();
  cache.set('movies', movies);
  return movies;
}

module.exports = { scrapeMovies };
