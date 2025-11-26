"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ClientesTendenciaChartProps {
  data: Array<{
    mes: string;
    clientes: number;
  }>;
}

export default function ClientesTendenciaChart({ data }: ClientesTendenciaChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <defs>
          <linearGradient id="colorClientes" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="mes" />
        <YAxis />
        <Tooltip />
        <Area
          type="monotone"
          dataKey="clientes"
          stroke="#8b5cf6"
          fillOpacity={1}
          fill="url(#colorClientes)"
          name="Nuevos Clientes"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

