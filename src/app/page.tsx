"use client";
import { useDropzone } from "react-dropzone";

import styles from "./page.module.css";
import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";

const getBase64 = async (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result?.toString()!);
    reader.onerror = (error) => reject(error);
  });
function fileSize(size: number) {
  const KB = 1024;
  const MB = KB * 1024;
  const GB = MB * 1024;

  if (size < KB) {
    return `${size} bytes`;
  } else if (size < MB) {
    return `${(size / KB).toFixed(2)} KB`;
  } else if (size < GB) {
    return `${(size / MB).toFixed(2)} MB`;
  } else {
    return `${(size / GB).toFixed(2)} GB`;
  }
}
export default function Home() {
  let [files, setFiles] = useState<File[]>([]);
  let router = useRouter();
  function removeFile(i: number) {
    files.splice(i, 1);
    setFiles(files);
  }
  async function submit() {
    let d1 = await getBase64(files[0]);
    let d2 = await getBase64(files[1]);

    const formData = new FormData();
    formData.append("d1", d1);
    formData.append("d2", d2);
    fetch("https://plagirsm-checker.vercel.app:4437/", {
      method: "POST",
      body: JSON.stringify({ d1: d1, d2: d2 }),
    })
      .then(async (response) => {
        let data = await response.json();
        localStorage.setItem("response", JSON.stringify(data));
        router.push("/result");
      })
      .then((data) => {})
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
        {files.length < 2 && (
          <div className={styles.info}>
            Upload two documents and know the percentage of plagiarism that both
            paper exhibits
          </div>
        )}

        <div
          className={`${styles.fileInp} ${files.length >= 1 ? styles.fileView : ""}`}
          {...getRootProps()}
        >
          <input {...getInputProps()} />
          {files.length > 0 ? (
            <div className={styles.filesParent}>
              {files.map((file, i) => {
                return (
                  <div key={file.name} className={styles.file}>
                    <div className={styles.filesInfo}>{file.name}</div>
                    <div className={styles.container}>
                      <div className={styles.filesSize}>
                        {fileSize(file.size)}
                      </div>
                      <button
                        onClick={(e) => {
                          removeFile(i);
                        }}
                        className={styles.remove}
                      >
                        x
                      </button>
                    </div>
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
