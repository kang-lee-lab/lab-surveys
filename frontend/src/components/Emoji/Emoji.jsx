import React from "react";
function Emoji(props) {
  return (
    <img
      src={require(`../../assets/images/${props.type}/${props.name}.svg`)}
      alt="ponyo"
      width={props.width}
      height={props.height}
      style={props.style ?? {}}
    />
  );
}

export default Emoji;
