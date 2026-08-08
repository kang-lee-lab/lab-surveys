import React from "react";
import Emoji from "../Emoji/Emoji";
import { SymbolEmoji } from "../../enums/Emojis";

function ArrowButton(props) {
  if (props.action === "back") {
    return (
      <button
        onClick={(e) => props.backPage(e)}
        disabled={props.disableBackButton}
      >
        <Emoji
          type={"symbols"}
          name={
            props.disableBackButton
              ? SymbolEmoji.LEFT_ARROW_DISABLED
              : SymbolEmoji.LEFT_ARROW
          }
          width={30}
          height={30}
        />
      </button>
    );
  } else {
    return (
      <button
        onClick={(e) => props.nextPage(e)}
        disabled={props.disableBackButton}
      >
        <Emoji
          type={"symbols"}
          name={
            props.disableBackButton
              ? SymbolEmoji.RIGHT_ARROW_DISABLED
              : SymbolEmoji.RIGHT_ARROW
          }
          width={30}
          height={30}
        />
      </button>
    );
  }
}

export default ArrowButton;
