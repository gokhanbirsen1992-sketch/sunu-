import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = { children: ReactNode; fallback?: ReactNode };
type State = { hasError: boolean; error: Error | null };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error("[Stage Error]", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div
            style={{
              position: "fixed",
              left: 24,
              bottom: 24,
              padding: "12px 16px",
              background: "rgba(248, 113, 113, 0.18)",
              border: "1px solid rgba(248, 113, 113, 0.5)",
              color: "#fecaca",
              fontFamily: "system-ui, sans-serif",
              fontSize: 12,
              borderRadius: 8,
              maxWidth: 420,
              zIndex: 999,
            }}
          >
            3D motor yüklenirken hata: {this.state.error?.message}
          </div>
        )
      );
    }
    return this.props.children;
  }
}
