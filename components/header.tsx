export function Header() {
  return (
    <header
      className="border-b sticky top-0 z-50 backdrop-blur-sm"
      style={{
        backgroundColor: "rgba(26, 26, 27, 0.95)",
        borderColor: "#343536",
      }}
    >
      <div className="container mx-auto px-4 py-4">
        <h1 className="text-2xl font-bold text-white">RedditRadar</h1>
      </div>
    </header>
  );
}
