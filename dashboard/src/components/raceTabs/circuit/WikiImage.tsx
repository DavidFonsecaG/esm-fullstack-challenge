import { useRecordContext } from "react-admin";
import { useEffect, useState } from "react";

export const WikiImage = ({ titleField = "name" }) => {
  const record = useRecordContext();
  const [imgSrc, setImgSrc] = useState("");

  useEffect(() => {
    if (!record) return;
    const pageTitle = record[titleField]?.replaceAll(" ", "_");

    fetch(
      `https://en.wikipedia.org/w/api.php?action=query&titles=${pageTitle}&prop=pageimages&format=json&pithumbsize=600&origin=*`
    )
      .then((res) => res.json())
      .then((data) => {
        console.log(pageTitle, data);
        const pages = data.query?.pages || {};
        const firstKey = Object.keys(pages)[0];
        const imageUrl = pages[firstKey]?.thumbnail?.source;
        if (imageUrl) setImgSrc(imageUrl);
      });
  }, [record, titleField]);

  if (!imgSrc) return <div>No image found</div>;

  return <img src={imgSrc} alt="Wikipedia" style={{ maxWidth: "100%", maxHeight: "200px" }} />;
};
