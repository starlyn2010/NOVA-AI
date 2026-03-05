import math
from typing import Dict, List


class DynamicMemory:
    """
    Sliding conversation memory optimized for low-resource environments.
    It keeps recent turns verbatim and compresses older turns into a summary
    when approaching the token budget.
    """

    def __init__(
        self,
        token_limit: int = 4096,
        preserve_recent_turns: int = 6,
        summary_soft_limit: int = 1200,
    ):
        self.token_limit = max(512, int(token_limit))
        self.preserve_recent_turns = max(2, int(preserve_recent_turns))
        self.summary_soft_limit = max(256, int(summary_soft_limit))
        self.summary = ""
        self.turns: List[Dict[str, str]] = []

    @staticmethod
    def estimate_tokens(text: str) -> int:
        if not text:
            return 0
        words = len(text.split())
        return max(1, int(math.ceil(words * 1.35)))

    def _total_tokens(self) -> int:
        summary_tokens = self.estimate_tokens(self.summary)
        turns_tokens = sum(self.estimate_tokens(t.get("content", "")) for t in self.turns)
        return summary_tokens + turns_tokens

    def add_turn(self, role: str, content: str) -> None:
        if not content:
            return
        self.turns.append({"role": role.strip().lower(), "content": content.strip()})
        self._compress_if_needed()

    def set_external_summary(self, external_summary: str) -> None:
        if not external_summary:
            return
        block = external_summary.strip()
        if not block:
            return
        if self.summary:
            self.summary = f"{self.summary}\n- {block}"
        else:
            self.summary = f"- {block}"
        self._truncate_summary()

    def _compress_if_needed(self) -> None:
        while self._total_tokens() > self.token_limit and len(self.turns) > self.preserve_recent_turns:
            old_turns = self.turns[:-self.preserve_recent_turns]
            self.turns = self.turns[-self.preserve_recent_turns :]
            compressed = self._build_summary_block(old_turns)
            if compressed:
                if self.summary:
                    self.summary = f"{self.summary}\n{compressed}"
                else:
                    self.summary = compressed

        # Last resort: trim oldest "recent" entries if still over budget.
        while self._total_tokens() > self.token_limit and self.turns:
            first = self.turns[0]
            content = first.get("content", "")
            if len(content) <= 160:
                self.turns.pop(0)
                continue
            first["content"] = content[:157] + "..."
        self._truncate_summary()

    def _truncate_summary(self) -> None:
        if self.estimate_tokens(self.summary) <= self.summary_soft_limit:
            return

        lines = [ln.strip() for ln in self.summary.splitlines() if ln.strip()]
        while lines and self.estimate_tokens("\n".join(lines)) > self.summary_soft_limit:
            lines.pop(0)
        self.summary = "\n".join(lines)

    def _build_summary_block(self, turns: List[Dict[str, str]]) -> str:
        if not turns:
            return ""

        lines = ["Resumen operativo acumulado:"]
        for turn in turns[-12:]:
            role = turn.get("role", "user").upper()
            text = turn.get("content", "").replace("\n", " ").strip()
            if len(text) > 180:
                text = text[:177] + "..."
            lines.append(f"- {role}: {text}")
        return "\n".join(lines)

    def build_prompt_context(self) -> str:
        parts = []
        if self.summary:
            parts.append(f"[MEMORIA_RESUMIDA]\n{self.summary}")
        if self.turns:
            rendered = []
            for turn in self.turns:
                role = turn.get("role", "user").upper()
                rendered.append(f"- {role}: {turn.get('content', '')}")
            parts.append("[MEMORIA_RECIENTE]\n" + "\n".join(rendered))
        return "\n\n".join(parts)
