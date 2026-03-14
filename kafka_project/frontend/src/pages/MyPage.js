// src/pages/MyPage.js
import React, { useEffect, useState } from "react";
import axios from "axios";

function MyPage() {
  const [coupons, setCoupons] = useState([]);
  const token = localStorage.getItem("access"); // JWT 액세스 토큰

  useEffect(() => {
    if (!token) return;

    axios
      .get("/api/coupon-list/", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((response) => {
        setCoupons(response.data);
      })
      .catch((error) => {
        console.error("쿠폰 조회 에러:", error);
      });
  }, [token]);

  return (
    <div>
      <h2>My Coupon List</h2>

      {coupons.length === 0 && <p>발급된 쿠폰이 없습니다.</p>}

      {coupons.map((item) => (
        <div key={item.id}>
          <p>유저 이름 : {item.username}</p>
          <p>이벤트명 : {item.event_title}</p>
          <p>코드번호 : {item.code}</p>
          <p>발급일자 : {item.issued_at}</p>
          <p>사용여부 : {item.is_used ? "사용불가" : "사용가능"}</p>
          <hr />
        </div>
      ))}
    </div>
  );
}

export default MyPage;

