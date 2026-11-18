# فصل ۱۱: خطا، اشکال‌زدایی و آزمون

نسخهٔ مستقل فصل؛ سند اصلی کتاب و فصل‌های تأییدشده ویرایش نشده‌اند.

## شروع سریع

دستورها را در ریشهٔ همین پوشه اجرا کنید. Python 3.11+ و کتابخانهٔ استاندارد برای پروژه کافی است.

```bash
python -m order_report
python -m unittest discover -s tests -v
python examples/run_examples.py
python examples/solutions.py
```

از پوشه‌ای دیگر، مسیر کامل run_analysis.py را به Python بدهید؛ دادهٔ پیش‌فرض نسبت به فایل پروژه پیدا می‌شود. مسیر ورودی نسبی ارسالی کاربر نسبت به پوشهٔ جاری است.

## کنترل‌های جداگانه

```bash
python -O -m unittest discover -s tests -v
python -m pip install -r requirements-qa.txt
python tests/check_notebook_kernel.py
python -m pytest -q examples/pytest_demo.py
python -m pdb examples/debug_demo.py
```

pdb تعاملی و فرمول debug_demo عمداً غلط است. pytest اختیاری است؛ نصب آن برای unittest اصلی لازم نیست. requirements-qa.txt قفل نسخه نیست. دفترچهٔ منتشرشده خروجی ذخیره‌شده ندارد؛ با کرنل تازه Run All شود.

## فایل‌ها

- chapter-11-fa.docx: نسخهٔ Word مستقل، متن فارسی و کد/خروجی LTR تک‌عرض.
- chapter-11-full-fa.md و .txt: متن کامل، برابر با یکدیگر.
- chapter-11-summary-fa.md: خلاصهٔ مرور.
- notebooks/11-errors-debugging-testing.ipynb: ۳۰ مثال آموزشی.
- examples/c01.py تا c30.py: مثال‌های مستقل؛ catalog.json مرجع خروجی‌ها.
- examples/problems.json و solutions.py: ۱۲ تمرین، شامل ۸ پاسخ کدنویسی.
- examples/intentional-errors.json و intentional-errors-fa.md: هشت خطای عمدی همراه اصلاح.
- order_report/: پروژهٔ پیوستهٔ CSV، اعتبارسنجی، تراز و مرز CLI.
- data/: همان دادهٔ مرجع فصل دهم؛ JSON فقط برای تطبیق رکوردهاست.
- outputs/report.txt: خروجی مرجع، بدون خط single_pass فصل دهم.
- tests/: مجموعهٔ اصلی آزمون و کنترل کرنل.
- SOURCE-MAP.md، TEST-REPORT.txt و qa-results/: منابع و شواهد کنترل کیفیت.
- MANIFEST.sha256: digest همهٔ فایل‌های نهایی به‌جز خودش؛ امضای دیجیتال نیست.

## قرارداد کوتاه

header دقیق، تاریخ canonical و دامنهٔ integer الزامی است. bool عدد قراردادی نیست. parsing از اعتبارسنجی دامنه جداست. تبدیل int الزام canonical برای متن عدد ندارد. رکورد خراب، گزارش موفق ناقص نمی‌سازد. پیام عمومی دادهٔ خام را نشان نمی‌دهد؛ traceback حالت debug ممکن است نشان دهد.

کد خروج موفق 0، خطای I/O شناخته‌شده 2 و خطای داده 3 است. argparse نیز برای آرگومان نامعتبر ممکن است 2 بدهد. باگ داخلی عمداً منتشر می‌شود. سهم کل صفر None و نمایش NA است. retained سود نیست.

کد و خروجی آموزشی ASCII هستند؛ پروژه اعتبارسنج عمومی ASCII برای ورودی سفارشی نیست. حافظهٔ ثابت، benchmark، نوشتن اتمیک، thread safety، تراکنش و صحت خارجی داده ادعا نشده‌اند. جزئیات آزمون و محیط‌های آزموده‌نشده در TEST-REPORT.txt آمده است.
