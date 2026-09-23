type ColorAwareImage = {
  colorId?: number;
};

export function selectImagesForColor<T extends ColorAwareImage>(
  images: T[],
  colorId: number,
): T[] {
  const colorImages = images.filter((image) => image.colorId === colorId);
  const generalImages = images.filter((image) => image.colorId === undefined);

  return [...colorImages, ...generalImages];
}
