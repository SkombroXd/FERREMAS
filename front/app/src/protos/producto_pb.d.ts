import * as jspb from 'google-protobuf'



export class CrearProductoRequest extends jspb.Message {
  getCodProducto(): string;
  setCodProducto(value: string): CrearProductoRequest;

  getNombreP(): string;
  setNombreP(value: string): CrearProductoRequest;

  getPrecioP(): number;
  setPrecioP(value: number): CrearProductoRequest;

  getUnidadesP(): number;
  setUnidadesP(value: number): CrearProductoRequest;

  getImagen(): Uint8Array | string;
  getImagen_asU8(): Uint8Array;
  getImagen_asB64(): string;
  setImagen(value: Uint8Array | string): CrearProductoRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CrearProductoRequest.AsObject;
  static toObject(includeInstance: boolean, msg: CrearProductoRequest): CrearProductoRequest.AsObject;
  static serializeBinaryToWriter(message: CrearProductoRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CrearProductoRequest;
  static deserializeBinaryFromReader(message: CrearProductoRequest, reader: jspb.BinaryReader): CrearProductoRequest;
}

export namespace CrearProductoRequest {
  export type AsObject = {
    codProducto: string,
    nombreP: string,
    precioP: number,
    unidadesP: number,
    imagen: Uint8Array | string,
  }
}

export class CrearProductoResponse extends jspb.Message {
  getExito(): boolean;
  setExito(value: boolean): CrearProductoResponse;

  getMensaje(): string;
  setMensaje(value: string): CrearProductoResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CrearProductoResponse.AsObject;
  static toObject(includeInstance: boolean, msg: CrearProductoResponse): CrearProductoResponse.AsObject;
  static serializeBinaryToWriter(message: CrearProductoResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CrearProductoResponse;
  static deserializeBinaryFromReader(message: CrearProductoResponse, reader: jspb.BinaryReader): CrearProductoResponse;
}

export namespace CrearProductoResponse {
  export type AsObject = {
    exito: boolean,
    mensaje: string,
  }
}

export class ListarProductosRequest extends jspb.Message {
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListarProductosRequest.AsObject;
  static toObject(includeInstance: boolean, msg: ListarProductosRequest): ListarProductosRequest.AsObject;
  static serializeBinaryToWriter(message: ListarProductosRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListarProductosRequest;
  static deserializeBinaryFromReader(message: ListarProductosRequest, reader: jspb.BinaryReader): ListarProductosRequest;
}

export namespace ListarProductosRequest {
  export type AsObject = {
  }
}

export class Producto extends jspb.Message {
  getCodProducto(): string;
  setCodProducto(value: string): Producto;

  getNombreP(): string;
  setNombreP(value: string): Producto;

  getPrecioP(): number;
  setPrecioP(value: number): Producto;

  getUnidadesP(): number;
  setUnidadesP(value: number): Producto;

  getImagen(): Uint8Array | string;
  getImagen_asU8(): Uint8Array;
  getImagen_asB64(): string;
  setImagen(value: Uint8Array | string): Producto;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Producto.AsObject;
  static toObject(includeInstance: boolean, msg: Producto): Producto.AsObject;
  static serializeBinaryToWriter(message: Producto, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Producto;
  static deserializeBinaryFromReader(message: Producto, reader: jspb.BinaryReader): Producto;
}

export namespace Producto {
  export type AsObject = {
    codProducto: string,
    nombreP: string,
    precioP: number,
    unidadesP: number,
    imagen: Uint8Array | string,
  }
}

export class ListarProductosResponse extends jspb.Message {
  getProductosList(): Array<Producto>;
  setProductosList(value: Array<Producto>): ListarProductosResponse;
  clearProductosList(): ListarProductosResponse;
  addProductos(value?: Producto, index?: number): Producto;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ListarProductosResponse.AsObject;
  static toObject(includeInstance: boolean, msg: ListarProductosResponse): ListarProductosResponse.AsObject;
  static serializeBinaryToWriter(message: ListarProductosResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ListarProductosResponse;
  static deserializeBinaryFromReader(message: ListarProductosResponse, reader: jspb.BinaryReader): ListarProductosResponse;
}

export namespace ListarProductosResponse {
  export type AsObject = {
    productosList: Array<Producto.AsObject>,
  }
}

