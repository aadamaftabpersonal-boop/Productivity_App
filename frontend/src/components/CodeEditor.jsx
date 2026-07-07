import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { java } from "@codemirror/lang-java";
import { tokyoNight } from "@uiw/codemirror-theme-tokyo-night";

const LANG_EXTENSIONS = {
  python: python(),
  cpp: cpp(),
  java: java(),
};

export default function CodeEditor({ value, onChange, language }) {
  return (
    <div className="rounded-lg overflow-hidden border border-border">
      {/* fake editor chrome — grounds it as "a code editor" visually, not just a text box */}
      <div className="flex items-center gap-1.5 bg-[#1a1b26] px-3 py-2 border-b border-border">
        <span className="w-2.5 h-2.5 rounded-full bg-tier-red/70" />
        <span className="w-2.5 h-2.5 rounded-full bg-tier-orange/70" />
        <span className="w-2.5 h-2.5 rounded-full bg-tier-green/70" />
        <span className="ml-2 text-xs text-muted font-mono">solution.{language === "python" ? "py" : language === "cpp" ? "cpp" : "java"}</span>
      </div>
      <CodeMirror
        value={value}
        height="360px"
        theme={tokyoNight}
        extensions={[LANG_EXTENSIONS[language] || python()]}
        onChange={onChange}
        basicSetup={{ lineNumbers: true, tabSize: 4 }}
      />
    </div>
  );
}