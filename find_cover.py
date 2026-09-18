#!/usr/bin/env python3
"""
بحث غلاف ترويجي رسمي لمشاهد Bratty Sis / Nubiles / Moms Teach Sex
الاستخدام:
  python3 find_cover.py "At Your Service Sis - S3:E5"
  python3 find_cover.py "It Just Slipped In"
"""

import sys
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def to_slug(title: str) -> str:
    """تحويل العنوان إلى slug مناسب لـ brattyfamily.com"""
    # إزالة الموسم/الحلقة
    title = re.sub(r'\s*[-–—]?\s*S\d+:E\d+.*$', '', title, flags=re.I)
    title = re.sub(r'\s*[-–—]?\s*Season\s*\d+.*$', '', title, flags=re.I)
    title = title.lower().strip()
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = re.sub(r'\s+', '-', title)
    title = re.sub(r'-+', '-', title).strip('-')
    return title

def to_underscore(title: str) -> str:
    return to_slug(title).replace('-', '_')

def try_brattyfamily(slug: str):
    """محاولة فتح صفحة brattyfamily واستخراج og:image"""
    urls = [
        f"https://brattyfamily.com/{slug}/",
        f"https://brattyfamily.com/{slug.replace('-', '_')}/",
    ]
    for url in urls:
        try:
            print(f"  جاري فحص: {url}")
            r = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            # og:image
            og = soup.find("meta", property="og:image")
            if og and og.get("content"):
                img = og["content"]
                if "wp-content/uploads" in img or "brattyfamily" in img:
                    return img, url
            # twitter:image
            tw = soup.find("meta", attrs={"name": "twitter:image"})
            if tw and tw.get("content"):
                return tw["content"], url
        except Exception as e:
            print(f"    خطأ: {e}")
    return None, None

def try_direct_images(slug_u: str, slug_k: str):
    """محاولة مسارات صور مباشرة شائعة"""
    candidates = []
    years = range(2017, 2027)
    months = [f"{m:02d}" for m in range(1, 13)]
    for y in years:
        for m in months:
            candidates.append(f"https://brattyfamily.com/wp-content/uploads/{y}/{m}/{slug_u}.jpg")
            candidates.append(f"https://brattyfamily.com/wp-content/uploads/{y}/{m}/{slug_k}.jpg")
            candidates.append(f"https://brattyfamily.com/wp-content/uploads/{y}/{m}/{slug_u}-1024x576.jpg")
            candidates.append(f"https://brattyfamily.com/wp-content/uploads/{y}/{m}/{slug_k}-1024x576.jpg")

    # Nubiles CDN
    candidates.extend([
        f"https://images.nubiles-porn.com/videos/{slug_k}/samples/cover1280.jpg",
        f"https://images.nubiles-porn.com/videos/{slug_u}/samples/cover1280.jpg",
        f"https://images.nubiles-porn.com/videos/{slug_k}/cover.jpg",
    ])

    for url in candidates:
        try:
            r = requests.head(url, headers=HEADERS, timeout=6, allow_redirects=True)
            if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                return url
        except:
            pass
    return None

def main():
    if len(sys.argv) < 2:
        print("الاستخدام: python3 find_cover.py \"اسم الحلقة\"")
        print("مثال: python3 find_cover.py \"At Your Service Sis - S3:E5\"")
        sys.exit(1)

    title = " ".join(sys.argv[1:]).strip()
    print(f"\n🔍 البحث عن غلاف ترويجي لـ: {title}\n")

    slug_k = to_slug(title)
    slug_u = to_underscore(title)
    print(f"Slug (kebab): {slug_k}")
    print(f"Slug (underscore): {slug_u}\n")

    # 1) صفحة brattyfamily
    print("① محاولة صفحة الحلقة على brattyfamily.com ...")
    img, page = try_brattyfamily(slug_k)
    if img:
        print(f"\n✅ تم العثور على الغلاف!")
        print(f"الصفحة: {page}")
        print(f"الصورة: {img}")
        return

    # 2) صور مباشرة
    print("\n② محاولة مسارات صور مباشرة ...")
    img = try_direct_images(slug_u, slug_k)
    if img:
        print(f"\n✅ تم العثور على صورة محتملة!")
        print(f"الصورة: {img}")
        print("⚠️ تحقق بالعين أنها غلاف ترويجي وليست ستيل داخلي.")
        return

    print("\n❌ لم يتم العثور على غلاف تلقائياً.")
    print("جرب:")
    print(f"  - https://brattyfamily.com/{slug_k}/")
    print(f"  - ابحث في Google: site:brattyfamily.com \"{title}\"")
    print(f"  - أو site:thenude.com \"{title}\" cover")

if __name__ == "__main__":
    main()
