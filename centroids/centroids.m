close all;
%152 PIXELS EQUIVALE A 25MM
%1 PIXEL EQUIVALE A 0.1645MM

load("cameraParams.mat");


%%
% Leitura da imagem binária
Ij = imread('teste35cm.jpeg');
Ioriginal = undistortImage(Ij, cameraParams); %tira a distorção da imagem

% Mostre a imagem original e a imagem corrigida
figure;
imshowpair(Ij, Ioriginal, 'montage');
title('Imagem Original (esquerda) e Imagem Corrigida (direita)');

%Transforma a imagem inicial para Cinza
I = rgb2gray(Ioriginal);

%Transforma para binário
limiar = graythresh(I);
ImagemC = imbinarize(I,limiar);
figure; imshow(ImagemC);



%Retira elementos de borda
ImagemC = imclearborder(ImagemC, 8);
figure; imshow(ImagemC);

%inverte a imagem
ImagemC = 1 - ImagemC;

%Retira elementos de borda
ImagemC = imclearborder(ImagemC, 8);
figure; imshow(ImagemC);

%Operação de Abertura
S = strel('disk',1);
ImagemC = imopen(ImagemC,S);
figure; imshow(ImagemC);

% Identificação de regiões
[imLabel,N] = bwlabel(ImagemC);

% Análise das regiões
info = cell(N,1);
for K = 1:N
    I2 = (imLabel==K);
    info{K} = analisa_regioes(I2);
end


% Inicialize um vetor para armazenar todas as áreas
areas = zeros(numel(info), 1);

% Itera sobre todas as células em info
for i = 1:numel(info)
    % Extrai a área da região atual e a armazena no vetor de áreas
    areas(i) = info{i}{1}.area;
end

% Calcula a média das áreas
media_areas = mean(areas);


% Itera sobre todas as células em info
for i = 1:numel(info)
    % Se a área da região atual for maior que a média,
    % define todos os pixels dessa região como zeros na imagem binária
    if info{i}{1}.area > media_areas || info{i}{1}.area < media_areas/3
        % Obtém a matriz binária correspondente à região atual
        I2 = imLabel == i;
        % Define todos os pixels dessa região como zeros na imagem binária
        ImagemC(I2) = 0;
    end
end

figure; imshow(ImagemC);


% Identificação de regiões
[imLabel,N] = bwlabel(ImagemC);

% Análise das regiões
info = cell(N,1);
for K = 1:N
    I2 = (imLabel==K);
    info{K} = analisa_regioes(I2);
end

figure; imshow(Ioriginal);
plot_bbs(info,1);
plot_bbs(info,2);
plot_bbs(info,3);
plot_bbs(info,4);

% Abre a imagem original
figure; 
imshow(Ioriginal);

% Inicializa vetor para armazenar as coordenadas dos centros
coordenadas = zeros(numel(info), 2);


% Itera sobre todas as células em info
for i = 1:numel(info)
    % Extrai o centroide da região atual
    centroide = info{i}{1}.centroide;
    % Extrai as coordenadas x e y do centroide
    x_centroide = centroide(2);
    y_centroide = centroide(1);
    coordenadas(i, :) = centroide;
    % Plota um ponto vermelho no centroide
    hold on;
    plot(x_centroide, y_centroide, 'ro', 'MarkerSize', 10, 'LineWidth', 2);
end

% Exibe a imagem com os pontos vermelhos nos centros das regiões
hold off;









 %%
%Analisa Regiões
%I = imagem binária

function [info] = analisa_regioes(I)

[imLabel,N] = bwlabel(I);
info = cell(N,1);

    for K = 1:N
        
        I2 = (imLabel==K);
        
        %boundingBox
        [v,u]=find(I2);

        vmin= min(v);
        umin= min(u);
        vmax= max(v);
        umax= max(u);
        
        info{K}.bb=[vmin,vmax,umin,umax];
        
        %Área
        m00 = numel(find(I2));
        info{K}.area=m00;
        
       
        %Centroide
        m10 = sum(u);
        m01 = sum(v);
        uc = m10/m00;
        vc = m01/m00;
        info{K}.centroide=[vc,uc];
        
        if m00>20
            %inercia elipse
            m20=sum((u-uc).^2);
            m02=sum((v-vc).^2);
            m11=sum((v-vc).*(u-uc));
            J=[m20,m11;m11,m02]; %matriz de inercia da região
            Je=(4/m00).*J; %matriz de inercia da elipse
            info{K}.inercia_elipse=Je;

            %razão
            [autovetores, autovalores] = eig(Je);
            info{K}.autovetores = autovetores;
            info{K}.autovalores = autovalores;
            valores=diag(autovalores);
            a = sqrt(valores(1));
            b = sqrt(valores(2));
            info{K}.razao=a/b;

            %angulo
            vetor2 = autovetores(:,2);
            info{K}.angulo = atan(vetor2(2)/vetor2(1))*180/pi;

            %Perimetro

            [linhas,colunas] = acha_borda(I2);
            aux=[linhas;colunas];
            info{K}.edge=aux;
            M=numel(linhas);
            perimetro = sqrt((colunas(M)-colunas(1))^2 +(linhas(M)-linhas(1))^2 );

            for L= 2:1:M
                distancia = sqrt((colunas(L)-colunas(L-1))^2 +(linhas(L)-linhas(L-1))^2 );
                perimetro = perimetro + distancia;
            end
            info{K}.perimetro = perimetro;

            %circularidade
            rho=(4*pi*m00/(perimetro^2));
            info{K}.circularidade = rho;

            %curva de Distância e ângulo
            [colunas,linhas]=f_interpolation(colunas,linhas,400);
            M=numel(linhas);
            d = zeros(1,M);
            A = zeros(1,M);
            for L= 1:1:M
                %curva de distancia e ângulo
                d(L) = sqrt((colunas(L)-uc)^2 +(linhas(L)-vc)^2 );
                A(L) = atan2((linhas(L)-vc),(colunas(L)-uc));
            end
            info{K}.curvadistancia=d;
            info{K}.curvaangulo=A;
        
        end
    end

end


%%
%Função acha borda

function [linhas, colunas]=acha_borda(I)
[v,u] = find(I);
coord = [v,u];
u_atual(1) = min(u);
linhas_com_minimo_u = coord(:, 2) == u_atual;
v_atual(1) = min(coord(linhas_com_minimo_u, 1));


u_anterior = u_atual-1;
v_anterior = v_atual;
u_final = u_atual;
v_final = v_atual;

cond = 1;
i=1;

while cond == 1
    i = i+1;
    P_avanco = 0;
    
    while P_avanco == 0
            
        if(u_anterior<u_atual(i-1))
        
            if(v_anterior<v_atual(i-1))
                u_avanco = u_anterior+1;
                v_avanco = v_anterior;
            end
            if(v_anterior==v_atual(i-1))
                u_avanco = u_anterior;
                v_avanco = v_anterior-1;
            end
            if(v_anterior>v_atual(i-1))
                u_avanco = u_anterior;
                v_avanco = v_anterior-1;

            end          
        end
     
        if(u_anterior==u_atual(i-1))
            if(v_anterior<v_atual(i-1))
                u_avanco = u_anterior+1;
                v_avanco = v_anterior;
            end           
            if(v_anterior>v_atual(i-1))
                u_avanco = u_anterior-1;
                v_avanco = v_anterior; 
            end
        end
        
        if(u_anterior>u_atual(i-1))
            if(v_anterior<v_atual(i-1))
                u_avanco = u_anterior;
                v_avanco = v_anterior+1;
            end
            if(v_anterior==v_atual(i-1))
                u_avanco = u_anterior;
                v_avanco = v_anterior+1;

            end
            if(v_anterior>v_atual(i-1))
                u_avanco = u_anterior-1;
                v_avanco = v_anterior;
            end
        end 
        
        P_avanco = I(v_avanco,u_avanco);
        if P_avanco == 0
            u_anterior = u_avanco;
            v_anterior = v_avanco;
        end
    end
    
     if u_avanco == u_final
         if v_avanco == v_final
            cond = 2;
         end 
     end 
     if cond == 1
      u_atual(i) = u_avanco;
      v_atual(i) = v_avanco;
     end
end
    linhas = v_atual;
    colunas = u_atual;
        
end
%%
%Função interpolação

function [new_cols, new_rows] = f_interpolation(u,v,num)

x = 1:numel(u);
xi = linspace(1,numel(u),num);

new_rows = interp1(x,v,xi,'linear','extrap');
new_cols = interp1(x,u,xi,'linear','extrap');


end

%%
%função similaridade

function similaridade = similaridadeCurvas(cDist1, cDist2)
    
    % Normalizacao:
    x1 = cDist1 - mean(cDist1);
    x2 = cDist2 - mean(cDist2);
    % Para deixar em escala proximas:
    y1 = x1/sqrt(sum(x1.^2));
    y2 = x2/sqrt(sum(x2.^2));
    
    % Desloca-se a curva y2 em 1 unidade para obter a maxima correlacao:
    corr = zeros(1,400);
    for k = 1:400
        y2 = circshift(y2,1);
        corr(k) = sum(y1.*y2);      
    end
    
    similaridade = max(corr);
    
end

%%
%Função plot bounding box

%info é uma célula
%a imagem tem que estar aberta
function [saida]=plot_bbs(info,indice)

   

        vmin=info{indice}{1}.bb(1);
        vmax=info{indice}{1}.bb(2);
        umin=info{indice}{1}.bb(3);
        umax=info{indice}{1}.bb(4);
        
        
        line([umin,umax],[vmin,vmin],'color','g','LineWidth',2);
        line([umin,umax],[vmax,vmax],'color','g','LineWidth',2);
        line([umax,umax],[vmin,vmax],'color','g','LineWidth',2);
        line([umin,umin],[vmin,vmax],'color','g','LineWidth',2);
        

    
    hold off;
end


