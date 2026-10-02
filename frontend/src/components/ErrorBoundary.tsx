import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught React Error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#0a0e1a] text-white flex items-center justify-center p-6">
          <div className="max-w-lg w-full bg-[#111827] border border-red-500/40 rounded-xl p-6 text-center shadow-2xl">
            <h2 className="text-xl font-bold text-red-400 mb-2">Control Room Render Error</h2>
            <p className="text-sm text-slate-300 mb-4 font-mono bg-[#0a0e1a] p-3 rounded text-left overflow-auto max-h-32">
              {this.state.error?.message || "Unknown rendering exception"}
            </p>
            <button
              onClick={() => {
                localStorage.clear();
                window.location.href = "/";
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded text-sm font-semibold transition"
            >
              Reset Session & Reload
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
