import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ProductosService } from '../services/productos.service';

@Component({
  selector: 'app-crearproducto',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './crearproducto.component.html',
  styleUrl: './crearproducto.component.css'
})
export class CrearproductoComponent {
  constructor(private productosService: ProductosService) {}

  async onSubmit(event: Event) {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const nombre = (form.elements.namedItem('nombre') as HTMLInputElement).value;
    const precio = parseFloat((form.elements.namedItem('precio') as HTMLInputElement).value);
    const imagenFile = (form.elements.namedItem('imagen') as HTMLInputElement).files?.[0];

    let imagenBase64: string | undefined = undefined;
    if (imagenFile) {
      // Redimensionar la imagen a un máximo de 800x800 píxeles
      imagenBase64 = await this.resizeImage(imagenFile, 800, 800);
    }

    const productoData = {
      cod_producto: '', // Se generará automáticamente en el backend
      nombre_p: nombre,
      precio_p: precio,
      unidades_p: 0, // Siempre 0 al crear
      imagen_p: imagenBase64
    };

    this.productosService.crearProducto(productoData).subscribe({
      next: (response) => {
        console.log('Respuesta:', response);
        if (response.exito) {
          alert('Producto creado: ' + response.mensaje);
          form.reset();
        } else {
          alert('Error: ' + response.mensaje);
        }
      },
      error: (error) => {
        console.error('Error:', error);
        alert('Error al crear el producto');
      }
    });
  }

  // Redimensiona la imagen antes de enviarla y la convierte a base64
  resizeImage(file: File, maxWidth: number, maxHeight: number): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const reader = new FileReader();

      reader.onload = (e: any) => {
        img.src = e.target.result;
      };

      img.onload = () => {
        let width = img.width;
        let height = img.height;
        if (width > maxWidth || height > maxHeight) {
          const aspect = width / height;
          if (width > height) {
            width = maxWidth;
            height = Math.round(maxWidth / aspect);
          } else {
            height = maxHeight;
            width = Math.round(maxHeight * aspect);
          }
        }
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx!.drawImage(img, 0, 0, width, height);
        canvas.toBlob((blob) => {
          if (!blob) return reject('No se pudo convertir la imagen');
          const fr = new FileReader();
          fr.onload = () => resolve(fr.result as string);
          fr.onerror = reject;
          fr.readAsDataURL(blob);
        }, 'image/jpeg', 0.8);
      };

      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }
}
