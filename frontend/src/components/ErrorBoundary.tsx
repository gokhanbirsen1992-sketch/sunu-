import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = {
  children: ReactNode;
  fallback?: ReactNode;
  label?: string;
};
type State = { hasError: boolean; error: Error | null };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error(`[${this.props.label ?? "ErrorBoundary"}]`, error, info);
  }

  render() {
    if (this.state.hasError) {
      const err = this.state.error;
      return (
        this.props.fallback ?? (
          <div
            style={{
              position: "fixed",
              left: 24,
              bottom: 24,
              padding: "14px 18px",
              background: "rgba(248, 113, 113, 0.18)",
              border: "1px solid rgba(248, 113, 113, 0.5)",
              color: "#fecaca",
              fontFamily: "ui-monospace, monospace",
              fontSize: 11,
              lineHeight: 1.45,
              borderRadius: 8,
              maxWidth: 600,
              maxHeight: "60vh",
              overflow: "auto",
              zIndex: 999,
              whiteSpace: "pre-wrap",
            }}
          >
            <strong style={{ display: "block", marginBottom: 6 }}>
              {this.props.label ?? "Hata"} yüklenirken hata
            </strong>
            <div>{err?.message}</div>
            {err?.stack && (
              <details style={{ marginTop: 8, opacity: 0.75 }}>
                <summary style={{ cursor: "pointer" }}>stack</summary>
                <pre style={{ fontSize: 10, marginTop: 6 }}>{err.stack}</pre>
              </details>
            )}
          </div>
        )
      );
    }
    return this.props.children;
  }
}
