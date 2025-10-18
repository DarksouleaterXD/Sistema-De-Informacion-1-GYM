export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          Bienvenido a SI1-Spartan
        </h1>
        <div className="text-center space-y-4">
          <p className="text-lg">🚀 Full Stack Application</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="p-6 border rounded-lg">
              <h2 className="text-xl font-semibold mb-2">Frontend</h2>
              <p className="text-gray-600">Next.js 14.2</p>
            </div>
            <div className="p-6 border rounded-lg">
              <h2 className="text-xl font-semibold mb-2">Backend</h2>
              <p className="text-gray-600">Django 5.0</p>
            </div>
            <div className="p-6 border rounded-lg">
              <h2 className="text-xl font-semibold mb-2">Database</h2>
              <p className="text-gray-600">PostgreSQL 15</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
