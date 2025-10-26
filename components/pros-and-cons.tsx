import { CheckCircle, XCircle, ExternalLink } from "lucide-react";

interface ProsAndConsProps {
  pros: [string, string | null][];
  cons: [string, string | null][];
}

export function ProsAndCons({ pros, cons }: ProsAndConsProps) {
  // Don't render if no pros or cons
  if ((!pros || pros.length === 0) && (!cons || cons.length === 0)) {
    return null;
  }

  return (
    <section
      className="rounded-xl p-6 shadow-lg"
      style={{ backgroundColor: "#272729" }}
    >
      <h2 className="text-xl font-semibold mb-6" style={{ color: "#d7dadc" }}>
        Pros and Cons
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Pros Column */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="h-5 w-5" style={{ color: "#22c55e" }} />
            <h3 className="text-lg font-semibold" style={{ color: "#22c55e" }}>
              Pros
            </h3>
          </div>
          
          {pros && pros.length > 0 ? (
            <div className="space-y-2">
              {pros.map(([proText, proUrl], index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 p-3 rounded-lg relative"
                  style={{ backgroundColor: "rgba(34, 197, 94, 0.1)" }}
                >
                  <CheckCircle className="h-4 w-4 mt-0.5 flex-shrink-0" style={{ color: "#22c55e" }} />
                  <div className="flex-1">
                    <p className="text-sm leading-relaxed" style={{ color: "#d7dadc" }}>
                      {proText}
                    </p>
                    {proUrl && (
                      <a
                        href={proUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="absolute top-2 right-2 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                        title="View original Reddit comment"
                      >
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm" style={{ color: "#818384" }}>
              No pros found in Reddit comments
            </p>
          )}
        </div>

        {/* Cons Column */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-4">
            <XCircle className="h-5 w-5" style={{ color: "#ef4444" }} />
            <h3 className="text-lg font-semibold" style={{ color: "#ef4444" }}>
              Cons
            </h3>
          </div>
          
          {cons && cons.length > 0 ? (
            <div className="space-y-2">
              {cons.map(([conText, conUrl], index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 p-3 rounded-lg relative"
                  style={{ backgroundColor: "rgba(239, 68, 68, 0.1)" }}
                >
                  <XCircle className="h-4 w-4 mt-0.5 flex-shrink-0" style={{ color: "#ef4444" }} />
                  <div className="flex-1">
                    <p className="text-sm leading-relaxed" style={{ color: "#d7dadc" }}>
                      {conText}
                    </p>
                    {conUrl && (
                      <a
                        href={conUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="absolute top-2 right-2 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                        title="View original Reddit comment"
                      >
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm" style={{ color: "#818384" }}>
              No cons found in Reddit comments
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
