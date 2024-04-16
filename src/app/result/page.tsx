"use client";
import { useEffect, useState } from "react";
import styles from "./result.module.css";
interface localStorageProps {
  val: number[];
  p: number;
}

export default function Page() {
  let [res, setRes] = useState<localStorageProps>({ val: [], p: 0 });
  useEffect(() => {
    setRes(JSON.parse(localStorage.getItem("response")!));
  }, []);
  return (
    <div className={styles.parent}>
      <div className={styles.percent}>
        <div className={styles.title}>The Files are</div>
        <div className="flex gap-[20px]">
          <span className={styles.p}>
            {" "}
            {res!.p}
            <sup>%</sup>
          </span>
          <div className={styles.title}>similar</div>
        </div>
      </div>
    </div>
  );
}
