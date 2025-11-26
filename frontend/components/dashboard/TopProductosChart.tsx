"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface TopProductosChartProps {
  data: Array<{
    nombre: string;
    cantidad: number;
  }>;
}

export default function TopProductosChart({ data }: TopProductosChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="nombre" type="category" width={100} />
        <Tooltip />
        <Bar dataKey="cantidad" fill="#3b82f6" name="Cantidad Vendida" />
      </BarChart>
    </ResponsiveContainer>
  );
}

