"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface IngresosChartProps {
  data: Array<{
    mes: string;
    ingresos: number;
    membresias: number;
    ventas: number;
  }>;
}

export default function IngresosChart({ data }: IngresosChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="mes" />
        <YAxis />
        <Tooltip
          formatter={(value: number) => `Bs. ${value.toLocaleString("es-BO")}`}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="ingresos"
          stroke="#3b82f6"
          strokeWidth={2}
          name="Total Ingresos"
        />
        <Line
          type="monotone"
          dataKey="membresias"
          stroke="#10b981"
          strokeWidth={2}
          name="Membresías"
        />
        <Line
          type="monotone"
          dataKey="ventas"
          stroke="#f59e0b"
          strokeWidth={2}
          name="Ventas"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

