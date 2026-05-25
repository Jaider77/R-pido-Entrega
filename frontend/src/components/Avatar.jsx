import React from "react";

export default function Avatar({ size = 40, src = null, alt = "Avatar" }) {
  const style = {
    width: size,
    height: size,
    borderRadius: "50%",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    background: "rgba(255,255,255,0.12)",
    color: "white",
    overflow: "hidden",
  };

  if (src) {
    return <img src={src} alt={alt} style={style} />;
  }

  return (
    <div style={style} aria-hidden>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
        width={Math.floor(size * 0.7)}
        height={Math.floor(size * 0.7)}
      >
        <path d="M12 12a4 4 0 100-8 4 4 0 000 8z" />
        <path d="M4 20a8 8 0 0116 0v1H4v-1z" />
      </svg>
    </div>
  );
}
