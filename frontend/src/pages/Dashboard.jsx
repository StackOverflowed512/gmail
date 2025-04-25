import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

function Dashboard() {
  const chartRefs = useRef({});

  const generateRandomData = (data, variation = 0.1) => {
    return data.map((value) => {
      const change = value * variation * (Math.random() - 0.5);
      return Math.max(0, value + change); // Ensure no negative values
    });
  };

  const updateChartData = (chart, newData) => {
    chart.data.datasets[0].data = newData;
    chart.update();
  };

  useEffect(() => {
    const initialData = {
      responseTime: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
        values: [2.5, 1.8, 3.2, 2.1, 2.8],
      },
      responseProbability: {
        labels: ["Morning", "Afternoon", "Evening", "Night"],
        values: [75, 85, 65, 45],
      },
      contentPerformance: {
        labels: ["Emails", "Newsletters", "Promotions", "Updates"],
        values: [88, 76, 82, 71],
      },
      optimization: {
        labels: ["Open Rate", "Click Rate", "Conversion", "Retention"],
        values: [45, 28, 15, 62],
      },
    };

    const commonOptions = {
      responsive: true,
      plugins: {
        legend: {
          labels: { color: "white" },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { color: "white" },
        },
        x: {
          ticks: { color: "white" },
        },
      },
    };

    const createChart = (canvasId, config) => {
      const ctx = document.getElementById(canvasId).getContext("2d");
      if (chartRefs.current[canvasId]) {
        chartRefs.current[canvasId].destroy();
      }
      chartRefs.current[canvasId] = new Chart(ctx, config);
    };

    const initializeCharts = () => {
      createChart("responseTimeChart", {
        type: "line",
        data: {
          labels: initialData.responseTime.labels,
          datasets: [
            {
              label: "Average Response Time (hours)",
              data: initialData.responseTime.values,
              borderColor: "rgba(75, 192, 192, 1)",
              fill: false,
            },
          ],
        },
        options: commonOptions,
      });

      createChart("responseProbabilityChart", {
        type: "bar",
        data: {
          labels: initialData.responseProbability.labels,
          datasets: [
            {
              label: "Response Probability (%)",
              data: initialData.responseProbability.values,
              backgroundColor: "rgba(153, 102, 255, 0.2)",
              borderColor: "rgba(153, 102, 255, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: commonOptions,
      });

      createChart("contentPerformanceChart", {
        type: "bar",
        data: {
          labels: initialData.contentPerformance.labels,
          datasets: [
            {
              label: "Content Performance",
              data: initialData.contentPerformance.values,
              backgroundColor: "rgba(75, 192, 192, 0.2)",
              borderColor: "rgba(75, 192, 192, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: commonOptions,
      });

      createChart("optimizationChart", {
        type: "bar",
        data: {
          labels: initialData.optimization.labels,
          datasets: [
            {
              label: "Optimization & Improvement",
              data: initialData.optimization.values,
              backgroundColor: "rgba(153, 102, 255, 0.2)",
              borderColor: "rgba(153, 102, 255, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: commonOptions,
      });
    };

    setTimeout(initializeCharts, 0); // Delay to ensure DOM is rendered

    const interval = setInterval(() => {
      const newData = {
        responseTime: generateRandomData(initialData.responseTime.values, 0.1),
        responseProbability: generateRandomData(
          initialData.responseProbability.values,
          0.05
        ),
        contentPerformance: generateRandomData(
          initialData.contentPerformance.values,
          0.07
        ),
        optimization: generateRandomData(initialData.optimization.values, 0.08),
      };

      if (chartRefs.current.responseTimeChart) {
        updateChartData(
          chartRefs.current.responseTimeChart,
          newData.responseTime
        );
      }
      if (chartRefs.current.responseProbabilityChart) {
        updateChartData(
          chartRefs.current.responseProbabilityChart,
          newData.responseProbability
        );
      }
      if (chartRefs.current.contentPerformanceChart) {
        updateChartData(
          chartRefs.current.contentPerformanceChart,
          newData.contentPerformance
        );
      }
      if (chartRefs.current.optimizationChart) {
        updateChartData(
          chartRefs.current.optimizationChart,
          newData.optimization
        );
      }
    }, 5000); // Update every 5 seconds

    return () => {
      clearInterval(interval);
      Object.values(chartRefs.current).forEach((chart) => chart.destroy());
    };
  }, []);

  return (
    <div
      id="dashboardContent"
      className="bg-[#121212] text-white p-6 flex flex-col h-[90%]"
    >
      <h2 className="text-2xl font-bold row-span-1 mb-6">Dashboard Overview</h2>
      <div className="grid grid-cols-2 flex-1 grid-row-2 gap-6 row-span-10 overflow-y-scroll  ">
        <div className="bg-[#1E1E1E] col-start-1 row-start-1 col-span-1 row-span-1 p-4 rounded-lg flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Response Time Analysis</h3>
          <div className="flex-grow">
            <canvas id="responseTimeChart" className="w-full h-full"></canvas>
          </div>
        </div>
        <div className="bg-[#1E1E1E] col-start-1 row-start-2 col-span-1 row-span-1 p-4 rounded-lg flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Response Probability</h3>
          <div className="flex-grow">
            <canvas id="responseProbabilityChart" className="w-full h-full"></canvas>
          </div>
        </div>

        <div className="bg-[#1E1E1E] col-start-2 row-start-1 col-span-1 row-span-1 p-4 rounded-lg flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Content Performance</h3>
          <div className="flex-grow">
            <canvas id="contentPerformanceChart" className="w-full h-full"></canvas>
          </div>
        </div>

        <div className="bg-[#1E1E1E] col-start-2 row-start-2 col-span-1 row-span-1 p-4 rounded-lg flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Optimization</h3>
          <div className="flex-grow">
            <canvas id="optimizationChart" className="w-full h-full"></canvas>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
