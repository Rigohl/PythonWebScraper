import csv
import os

def generate_dummy_frontier_dataset(output_path: str = "data/frontier_dataset.csv", num_samples: int = 100):
    """
    Genera un dataset dummy para el FrontierClassifier.
    En una implementación real, esto recolectaría datos de URLs reales.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['url', 'path_depth', 'query_param_count', 'is_https', 'is_promising']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(num_samples):
            url = f"http://example.com/path{i % 5}/subpath{i % 10}?param={i}"
            path_depth = i % 5
            query_param_count = 1
            is_https = i % 2
            is_promising = 1 if i % 3 == 0 else 0 # Dummy promising logic

            writer.writerow({
                'url': url,
                'path_depth': path_depth,
                'query_param_count': query_param_count,
                'is_https': is_https,
                'is_promising': is_promising
            })
    print(f"Dummy frontier dataset generated at {output_path} with {num_samples} samples.")

if __name__ == "__main__":
    generate_dummy_frontier_dataset()
