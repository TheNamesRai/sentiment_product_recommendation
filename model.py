from pathlib import Path
from typing import Optional
import json, pickle

DATA_DIR = (Path(__file__).resolve().parent / "deployment")

class EbussRecommender:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self._load()

    def _p(self, name: str) -> Path:
        p = self.data_dir / name
        if not p.exists():
            raise FileNotFoundError(f"Missing {p}. Copy artifacts into deployment/")
        return p

    def _load(self) -> None:
        with open(self._p("sentiment.pkl"), "rb") as f:
            art = pickle.load(f)
        self.vectorizer = art["vectorizer"]
        self.model = art["model"]

        self.user_top20 = json.load(open(self._p("user_top20.json")))
        self.user_top5  = json.load(open(self._p("user_top5.json")))
        self.mappings   = json.load(open(self._p("mappings.json")))
        self.meta       = json.load(open(self._p("recommender_meta.json")))
        self.id_to_name = self.mappings.get("id_to_name", {})

    # -------- public API --------
    def available_users(self, limit: int = 50):
        return list(self.user_top5.keys())[:limit]

    def get_top20(self, username: str):
        return self.user_top20.get(username, [])

    def get_top5(self, username: str):
        return self.user_top5.get(username, [])

    def product_name(self, pid: str) -> str:
        return self.id_to_name.get(pid, pid)

    def sentiment(self, text: str):
        X = self.vectorizer.transform([text or ""])
        p = float(self.model.predict_proba(X)[:, 1][0])
        return {"prob_positive": p, "label": int(p >= 0.5)}

if __name__ == "__main__":
    svc = EbussRecommender()
    u = next(iter(svc.user_top5))
    print("example user:", u)
    print("top5 ids:", svc.get_top5(u))
    print("top5 names:", [svc.product_name(x) for x in svc.get_top5(u)])
