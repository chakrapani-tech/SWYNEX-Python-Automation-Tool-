# Example usage

This folder is intended for demonstration inputs and sample walkthroughs.

Use the generated sample data script to create a realistic test set:

```powershell
python scripts\generate_sample_data.py
python main.py --source .\input --destination .\organized --dry-run
python main.py --source .\input --destination .\organized --execute
python dashboard.py
```

Files are placed below category directories such as `organized\Documents` and `organized\Images`. Open <http://127.0.0.1:5000/> to review generated reports. The sample `photo.jpg` contains placeholder bytes and is classified by its `.jpg` suffix; it is not decoded or treated as a valid image.
