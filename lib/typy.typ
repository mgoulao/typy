#let init_typy(data) = {
  let typy(id, type) = {
    if (type == "str") {
      if (data.keys().contains(id)) {
        return data.at(id)
      } else {
        return "<Missing 'str' Key: " + id + ">"
      }
    } else {
      if (data.keys().contains(id)) {
        return data.at(id)
      } else {
        return box(
          height: 100%,
          width: 100%,
          stroke: rgb(255, 0, 0),
          align(horizon + center, [Missing 'content' for key: #id])
        )
      }
    }
  }
  return typy
}