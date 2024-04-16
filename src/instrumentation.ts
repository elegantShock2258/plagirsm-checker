import { spawn } from "child_process";
// Path to your Python script
const pythonScriptPath = "src/server/server.py";
export async function register() {
  const pythonProcess = spawn("python3", [pythonScriptPath], {
    detached: false,
    // stdio: "ignore", // Ignore stdio (standard input/output/error)
  });
  pythonProcess.on("error", (err) => {
    console.error("Failed to start Python Server:", err);
  });

  // Once the Python process is spawned, it will run independently in the background
  pythonProcess.unref();
  console.log("Python Server Started");
}
