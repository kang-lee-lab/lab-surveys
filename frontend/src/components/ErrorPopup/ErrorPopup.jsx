import React from "react";
import "./ErrorPopup.css";
import Emoji from "../Emoji/Emoji";
import { SymbolEmoji } from "../../enums/Emojis";

function ErrorPopup(props) {
  return (
    <div className="error-popup-container">
      {props.message}
      <button onClick={() => props.setShowError(false)}>
        <Emoji
          type={"symbols"}
          name={SymbolEmoji.RED_MULTIPLY}
          width={20}
          height={20}
          style={{
            paddingTop: `7px`,
            padding: "0",
            margin: "0",
          }}
        />
      </button>
    </div>
  );
}

export default ErrorPopup;
