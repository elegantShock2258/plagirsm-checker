"use client";
import { useDropzone } from "react-dropzone";

import styles from "./page.module.css";
import { useCallback, useState } from "react";

const getBase64 = async (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result?.toString()!);
    reader.onerror = (error) => reject(error);
  });

export default function Home() {
  let [files, setFiles] = useState<File[]>([]);
  async function submit() {
    let d1 = await getBase64(files[0]);
    let d2 = await getBase64(files[1]);

    const formData = new FormData();
    formData.append("d1", d1);
    formData.append("d2", d2);

    fetch("http://localhost:4437", {
      method: "POST",
      mode: "no-cors",
      body: JSON.stringify({ d1: d1, d2: d2 }),
    })
      .then((response) => {
        console.log(response);
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        console.log(data);
        localStorage.setItem("response", JSON.stringify(data));
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
      });
  }
  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 2) {
        // notify error
      }
      acceptedFiles.forEach((file) => {
        if (files.length < 2) files.push(file);
      });
      setFiles(files);
    },
    [files],
  );
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });
  return (
    <>
      <div className={styles.parent}>
        <div className={styles.title}>PLAGIARISM CHECKER</div>
        <div className={styles.info}>
          Upload two documents and know the percentage of plagiarism that both
          paper exhibits
        </div>

        <div className={styles.fileInp} {...getRootProps()}>
          <input {...getInputProps()} />
          {files.length > 0 ? (
            <div className={styles.filesParent}>
              {files.map((file) => {
                return (
                  <div key={file.name} className={styles.filesInfo}>
                    {file.name}
                  </div>
                );
              })}
            </div>
          ) : (
            <p>Drag {`'n'`} drop some files here, or click to select files</p>
          )}
        </div>
        {files.length === 2 && (
          <button
            onClick={async (e) => submit()}
            className={styles.submitButton}
          >
            Submit
          </button>
        )}
      </div>
    </>
  );
}
