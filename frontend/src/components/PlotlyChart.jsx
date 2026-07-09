import { useEffect, useRef, Component } from "react";

class ChartErrorBoundary extends Component {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError) return (
      <div className="flex items-center justify-center p-6">
        <p className="text-slate-500 text-sm">Chart unavailable</p>
      </div>
    );
    return this.props.children;
  }
}

function PlotDiv({ figure, height }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!ref.current || !figure?.data) return;
    import("plotly.js/dist/plotly").then(Plotly => {
      const P = Plotly.default || Plotly;
      P.newPlot(ref.current, figure.data, {
        ...figure.layout,
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        font: { color: "#94a3b8", size: 12 },
        margin: { t: 48, l: 56, r: 24, b: 48 },
        xaxis: { ...figure.layout?.xaxis, gridcolor: "#1e293b" },
        yaxis: { ...figure.layout?.yaxis, gridcolor: "#1e293b" },
        colorway: ["#38bdf8","#818cf8","#34d399","#fbbf24","#f472b6"],
        autosize: true,
      }, { displayModeBar: false, responsive: true });
    }).catch(() => {});

    return () => {
      import("plotly.js/dist/plotly").then(Plotly => {
        const P = Plotly.default || Plotly;
        if (ref.current) P.purge(ref.current);
      }).catch(() => {});
    };
  }, [figure]);

  return <div ref={ref} style={{ width: "100%", height: `${height}px` }} />;
}

export default function PlotlyChart({ figure, title, height = 320 }) {
  if (!figure || !figure.data) return null;
  return (
    <ChartErrorBoundary>
      <PlotDiv figure={figure} height={height} />
    </ChartErrorBoundary>
  );
}