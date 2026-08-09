import React from "react";
import "./Profile.css";

function Profile() {
  const user = JSON.parse(
    localStorage.getItem("currentUser")
  );

  return (
    <div className="profile-page">

      <div className="profile-heading">
        <p>ACCOUNT</p>
        <h1>My Profile</h1>
      </div>

      <div className="profile-card">

        <div className="profile-avatar">
          {user?.name?.charAt(0).toUpperCase()}
        </div>

        <h2>{user?.name}</h2>

        <p>{user?.email}</p>

        <div className="profile-info">

          <div>
            <span>Name</span>
            <strong>{user?.name}</strong>
          </div>

          <div>
            <span>Email</span>
            <strong>{user?.email}</strong>
          </div>

        </div>

      </div>

    </div>
  );
}

export default Profile;