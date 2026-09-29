"""
Ethical and Anti-Bot Guard for Airline & OTA Web Scraping.
Ensures:
1. robots.txt compliance checking
2. User-Agent rotation with realistic desktop fingerprints
3. Polite rate-limiting with randomized jitter
4. Session header simulation to avoid bot blocks
"""

import time
import random
import logging
import urllib.robotparser
from urllib.parse import urlparse
from typing import Dict, Optional
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EthicalGuard")

class EthicalGuard:
    def __init__(self, default_min_delay: float = 2.0, default_max_delay: float = 5.0):
        self.min_delay = default_min_delay
        self.max_delay = default_max_delay
        self.last_request_time: Dict[str, float] = {}
        self.robot_parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}
        try:
            self.ua_generator = UserAgent(browsers=['chrome', 'edge', 'firefox'])
        except Exception:
            self.ua_generator = None

        # Fallback realistic user agents
        self.fallback_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        ]

    def get_random_user_agent(self) -> str:
        """Returns a realistic, modern desktop browser user agent."""
        if self.ua_generator:
            try:
                return self.ua_generator.random
            except Exception:
                pass
        return random.choice(self.fallback_user_agents)

    def get_stealth_headers(self, origin_domain: str = "google.com") -> Dict[str, str]:
        """Generates authentic browser HTTP request headers."""
        return {
            "User-Agent": self.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }

    def can_fetch(self, target_url: str, user_agent: str = "*") -> bool:
        """
        Parses and verifies robots.txt for the given target URL.
        Falls back to permissive if robots.txt is unreachable/timeout.
        """
        parsed = urlparse(target_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain not in self.robot_parsers:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{domain}/robots.txt"
            rp.set_url(robots_url)
            try:
                rp.read()
                self.robot_parsers[domain] = rp
                logger.info(f"Loaded robots.txt from {domain}")
            except Exception as e:
                logger.warning(f"Could not load robots.txt for {domain}: {e}. Proceeding with polite defaults.")
                return True
        
        allowed = self.robot_parsers[domain].can_fetch(user_agent, target_url)
        return allowed if allowed is not None else True

    def polite_wait(self, domain: str):
        """
        Enforces polite crawl rate-limiting with randomized jitter.
        Prevents hitting servers with high-frequency bot bursts.
        """
        now = time.time()
        last = self.last_request_time.get(domain, 0)
        delay = random.uniform(self.min_delay, self.max_delay)
        elapsed = now - last
        
        if elapsed < delay:
            sleep_time = delay - elapsed
            logger.info(f"[Polite Guard] Waiting {sleep_time:.2f}s before fetching {domain}")
            time.sleep(sleep_time)
            
        self.last_request_time[domain] = time.time()
