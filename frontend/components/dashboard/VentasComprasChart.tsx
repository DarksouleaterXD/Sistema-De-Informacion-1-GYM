"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface VentasComprasChartProps {
  data: Array<{
    mes: string;
    ventas: number;
    compras: number;
  }>;
}

export default function VentasComprasChart({ data }: VentasComprasChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="mes" />
        <YAxis />
        <Tooltip
          formatter={(value: number) => `Bs. ${value.toLocaleString("es-BO")}`}
        />
        <Legend />
        <Bar dataKey="ventas" fill="#10b981" name="Ventas" />
        <Bar dataKey="compras" fill="#ef4444" name="Compras" />
      </BarChart>
    </ResponsiveContainer>
  );
}

