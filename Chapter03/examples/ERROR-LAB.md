# آزمایش خطاهای عمدی

این نمونه‌ها برای اجرای دفترچهٔ اصلی نیستند. هر نمونه را جدا و در فضای نام تازه اجرا کنید. برای E01 انتظار خطای نحوی داریم؛ برای بقیه، خطای هنگام اجرا. متن دقیق پیام به نسخه وابسته است.

## E01 — `SyntaxError`

```python
print(3 * 240_000
```

## E02 — `NameError`

```python
print(unregistered_quantity)
```

## E03 — `TypeError`

```python
print("3" + 2)
```

## E04 — `ValueError`

```python
print(int("3.0"))
```

## E05 — `ZeroDivisionError`

```python
refund_amount_toman = 0
initial_amount_toman = 0
print(refund_amount_toman / initial_amount_toman)
```

## E06 — `TypeError`

```python
shipping_cost_toman = None
print(480_000 + shipping_cost_toman)
```

